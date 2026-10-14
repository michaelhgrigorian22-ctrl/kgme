"""`kgme clean`, the filesystem effects: hash, final check, unlink, rmdir, payload write.

Purpose: the few places the deleter changes or reads the bytes of the world (HANDOFF-0033,
rebuilt to first principles on Michou's override of 2026-10-13: no descriptor chains, no
hold under a private name, no restore). Every operation is by plain pathname. Immediately
before an `unlink` or `rmdir`, `read_final_check` asks once more what the plan asked: the
path still resolves where the plan resolved it, so no component became a link; it is not a
link; it is the
device and inode the plan listed; a file still has the size and modification time the plan
listed. Any difference refuses the deletion. A file's hash is read once, before the intent,
through a descriptor opened without following a link and matched to the plan the same way.
The payload is created new, never through a link, and written whole or not at all (F8, F10).
Accepted residual risk, stated for review: a process writing through a descriptor it
already holds, or swapping the entry, between the final check and the `unlink`, is not
defended against; the outcome's hash is the hash taken before the intent.
Inputs: absolute paths under the checkout and the `Entry` the plan listed for each.
Outputs: sha256 prefixes, or nothing; `Refused` with a reason when the path is not what the
plan listed.
Side effects: `read_digest` opens and reads a file; `read_final_check` stats a path;
`run_unlink` and `run_rmdir` delete one entry; `read_bound_directory` opens a directory and
`write_payload` creates directories and one file inside it (F8); `write_lock` creates and
locks `kgme-clean.lock` in the git directory (F15). Descriptors other than the lock's are
closed before each returns.
"""

import errno
import fcntl
import hashlib
import os
import stat
from pathlib import Path

from kgme.clean import Entry
from kgme.clean_read import read_link_in_ancestry

NEW_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
LOCK_NAME = "kgme-clean.lock"


class Refused(Exception):
    """The path is not what the plan listed; the reason is the message."""


def _same(status: os.stat_result, entry: Entry) -> str:
    """Why `status` is not the entry the plan listed, or an empty string when it is."""
    if (status.st_dev, status.st_ino) != (entry.dev, entry.ino):
        return "replaced since the plan was made"
    if stat.S_ISDIR(status.st_mode) != entry.is_dir:
        return "not the kind of entry the plan saw"
    if not entry.is_dir and (status.st_size, status.st_mtime_ns) != (entry.size, entry.mtime_ns):
        return "changed since the plan was made"
    return ""


def read_digest(path: Path, entry: Entry) -> str:
    """The sha256 prefix of the file at `path`, opened without following a link and without
    waiting (a FIFO cannot hold the run, review cycle 5 F16), refused unless it is a regular
    file, and matched by `fstat` to the plan's entry before it is read."""
    try:
        fd = os.open(path, READ_FLAGS)
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise Refused("is a symlink") from error
        if error.errno == errno.ENOENT:
            raise Refused("is gone") from error
        raise
    try:
        status = os.fstat(fd)
        if not stat.S_ISREG(status.st_mode):
            raise Refused("not a regular file")
        reason = _same(status, entry)
        if reason:
            raise Refused(reason)
        digest = hashlib.sha256()
        while chunk := os.read(fd, 1 << 20):
            digest.update(chunk)
        return digest.hexdigest()[:16]
    finally:
        os.close(fd)


def read_final_check(path: Path, entry: Entry) -> None:
    """The last look before a deletion; `Refused` when the path is not what the plan listed."""
    try:
        status = os.lstat(path)
    except FileNotFoundError as error:
        raise Refused("is gone") from error
    if stat.S_ISLNK(status.st_mode):
        raise Refused("is a symlink")
    if Path(os.path.realpath(path)) != entry.resolved:
        raise Refused("a component of its path is a symlink")
    reason = _same(status, entry)
    if reason:
        raise Refused(reason)


def run_unlink(path: Path, entry: Entry) -> None:
    """The file the plan listed at `path`, checked a last time and unlinked."""
    read_final_check(path, entry)
    os.unlink(path)


def run_rmdir(path: Path, entry: Entry) -> None:
    """The empty directory the plan listed at `path`, checked a last time and removed."""
    read_final_check(path, entry)
    os.rmdir(path)


def write_whole(fd: int, data: bytes) -> None:
    """Every byte of `data` written to `fd`, however many calls that takes, then fsynced and
    its size checked; `OSError` when it cannot be."""
    view = memoryview(data)
    done = 0
    while done < len(data):
        count = os.write(fd, view[done:])
        if count <= 0:
            raise OSError(errno.EIO, "write returned nothing")
        done += count
    os.fsync(fd)
    if os.fstat(fd).st_size != len(data):
        raise OSError(errno.EIO, "size differs after the write")


def read_no_link_above(path: Path, root: Path) -> None:
    """`Refused` when any component of `path`'s directory below `root` is a symlink."""
    link = read_link_in_ancestry(path.parent, root)
    if link is not None:
        raise Refused(f"{link.relative_to(root)} is a symlink")


def read_bound_directory(directory: Path, root: Path) -> int:
    """A descriptor on `directory`, checked after it is opened: no component below `root` is a
    link and the path still names the directory the descriptor holds. A swap before the open
    is caught by the check; a swap after it cannot move what the descriptor holds (review
    cycle 5 F8). The caller closes it."""
    try:
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as error:
        raise Refused(f"could not be opened: {error.strerror}") from error
    try:
        read_no_link_above(directory / "x", root)
        held, named = os.fstat(fd), os.lstat(directory)
        if Path(os.path.realpath(directory)) != directory or (held.st_dev, held.st_ino) != (
            named.st_dev,
            named.st_ino,
        ):
            raise Refused("changed while it was opened")
    except (Refused, OSError):
        os.close(fd)
        raise
    return fd


def write_payload(root: Path, path: Path, text: str) -> None:
    """Create `path` under `root`, making its directories, inside a directory descriptor
    checked after it was opened; the file is new and written whole, or removed and
    refused."""
    read_no_link_above(path, root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise Refused(f"could not be made: {error.strerror}") from error
    dir_fd = read_bound_directory(path.parent, root)
    try:
        try:
            fd = os.open(path.name, NEW_FILE_FLAGS, 0o644, dir_fd=dir_fd)
        except OSError as error:
            raise Refused(f"{path.name}: {error.strerror}") from error
        try:
            write_whole(fd, text.encode("utf-8"))
        except OSError as error:
            os.close(fd)
            os.unlink(path.name, dir_fd=dir_fd)
            raise Refused(f"{path.name} could not be written whole: {error.strerror}") from error
        os.close(fd)
    finally:
        os.close(dir_fd)


def read_git_dir(base: Path) -> Path:
    """The checkout's git directory: `.git` itself, or the one a worktree's `.git` file names."""
    dot_git = base / ".git"
    if dot_git.is_dir():
        return dot_git
    pointer = dot_git.read_text(encoding="utf-8").strip()
    return (base / pointer.removeprefix("gitdir:").strip()).resolve()


def write_lock(base: Path) -> int | None:
    """Take `kgme-clean.lock` in the git directory, which no target reaches, without waiting;
    None when another run holds it. One run at a time means an open intent with no holder
    belongs to a run that ended (review cycle 5 F15). The kernel releases the lock when its
    holder exits, however it exits; the caller closes the descriptor."""
    fd = os.open(read_git_dir(base) / LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    return fd
