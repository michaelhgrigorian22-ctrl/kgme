"""`kgme capture` and `kgme daily`, the filesystem effects: the lock, the replace, the publish.

Purpose: the three ways the two jobs touch the vault's bytes (HANDOFF-0050). `write_lock`
serialises every capture and daily run over the vault, so an open intent with no holder
belongs to a run that ended. `write_replaced` adds a line to an existing file by replacing it
whole: the file read on a descriptor, the new bytes written to a temp file beside it and
fsynced, then the two names exchanged in one step, so the file holds its old bytes or its
new ones and a torn line cannot exist (the arbiter's ruling after AUDIT-0062, F10: remove
the mechanism). The displaced file is then read: if a writer outside the lock (an editor)
saved after the read, the exchange is undone and the capture refused (review cycle 5 F13).
Capture deletes nothing, ever (the rulings on cycle 6 F13 and F15, option A, with Cowork's
refinement): the temp file is named with the intent id (`kept_name`), and after the exchange
that name holds the displaced copy, which stays until `kgme clean kept` finds its bytes still
the ones the capture recorded.
`write_new` publishes a whole file under a name that must not exist: written to a temp file
beside it, fsynced, then `link`ed into place, which fails on an existing name and never
replaces, so the destination is absent or complete, never partial (review cycle 1 F1).
Inputs: the checkout, the destination, the text or a function from the current bytes to the
bytes added.
Outputs: a lock descriptor or None; the bytes added; nothing.
Side effects: the lock file in the git directory; one file replaced or created; the kept
copy left beside a replaced file; a temp file created and removed beside a new one.
"""

import ctypes
import errno
import fcntl
import os
import re
import stat
import time
from collections.abc import Callable
from pathlib import Path

from kgme import clean_fs, events

LOCK_NAME = "kgme-vault.lock"
LOCK_WAIT_SECONDS = 10.0
KEPT_NAME = re.compile(r"^\.(?P<name>.+)\.capture-(?P<id>[0-9A-HJKMNP-TV-Z]{26})$")
EXCHANGE = 2  # RENAME_SWAP (macOS `renameatx_np`) and RENAME_EXCHANGE (Linux `renameat2`)


def write_lock(base: Path, wait: float) -> int | None:
    """Take `kgme-vault.lock` in the git directory, asking again for up to `wait` seconds;
    None when another capture or daily run still holds it. The kernel releases it when its
    holder exits; the caller closes the descriptor."""
    fd = os.open(clean_fs.read_git_dir(base) / LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + wait
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.monotonic() >= deadline:
                os.close(fd)
                return None
            time.sleep(0.1)


def kept_name(name: str, intent_id: str) -> str:
    """The dotfile beside `name` that keeps what the replace under `intent_id` displaced."""
    return f".{name}.capture-{intent_id}"


def write_exchanged(dir_fd: int, first: str, second: str) -> None:
    """Exchange two existing names in one directory in one step; `OSError` when the system
    cannot (no exchange call, or either name missing)."""
    libc = ctypes.CDLL(None, use_errno=True)
    call = getattr(libc, "renameatx_np", None) or getattr(libc, "renameat2", None)
    if call is None:
        raise OSError(errno.ENOSYS, "no atomic exchange of names on this system")
    call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    if call(dir_fd, os.fsencode(first), dir_fd, os.fsencode(second), EXCHANGE) != 0:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number))


def read_name(dir_fd: int, name: str) -> bytes | None:
    """The bytes of the regular file `name` in the directory, never through a link; None
    when it is anything else."""
    try:
        fd = os.open(name, clean_fs.READ_FLAGS, dir_fd=dir_fd)
    except OSError:
        return None
    try:
        size = os.fstat(fd).st_size
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        return os.pread(fd, size + 1, 0)
    finally:
        os.close(fd)


def write_replaced(
    base: Path,
    path: Path,
    build: Callable[[bytes], str | bytes],
    announce: Callable[[int, bytes, bytes], str],
) -> bytes:
    """Replace `path` whole by its current bytes followed by what `build` makes of them:
    read it (a regular file, never through a link), build, `announce` (the offset, the bytes
    added, the bytes read; it returns the intent id), write the new bytes to the kept name
    beside it whole and fsynced with its mode, exchange the two names, and read what was
    displaced. When it is not exactly what was read, an editor saved meanwhile: the names are
    exchanged back and the capture refused, naming the kept file, which then holds the
    capture's own bytes, or those and a save made during the exchange. Nothing is removed on
    any path. The caller holds the lock and has checked the manifest. Returns the bytes
    added."""
    rel = path.relative_to(base).as_posix()
    clean_fs.read_no_link_above(path, base)
    dir_fd = clean_fs.read_bound_directory(path.parent, base)
    try:
        try:
            fd = os.open(path.name, clean_fs.READ_FLAGS, dir_fd=dir_fd)
        except OSError as error:
            if error.errno == errno.ELOOP:
                raise clean_fs.Refused(f"{rel} is a symlink") from error
            raise clean_fs.Refused(f"{rel} could not be opened: {error.strerror}") from error
        try:
            status = os.fstat(fd)
            if not stat.S_ISREG(status.st_mode):
                raise clean_fs.Refused(f"{rel} is not a regular file")
            existing = os.pread(fd, status.st_size, 0)
        finally:
            os.close(fd)
        if len(existing) != status.st_size:
            raise clean_fs.Refused(f"{rel} changed while it was read")
        made = build(existing)
        added = made.encode("utf-8") if isinstance(made, str) else made
        kept = kept_name(path.name, announce(len(existing), added, existing))
        out = os.open(kept, clean_fs.NEW_FILE_FLAGS, 0o600, dir_fd=dir_fd)
        try:
            os.fchmod(out, stat.S_IMODE(status.st_mode))
            clean_fs.write_whole(out, existing + added)
        finally:
            os.close(out)
        write_exchanged(dir_fd, kept, path.name)
        if read_name(dir_fd, kept) != existing:
            write_exchanged(dir_fd, kept, path.name)
            if read_name(dir_fd, kept) != existing + added:
                raise clean_fs.Refused(
                    f"kept {kept} beside {rel}: another writer saved during the capture; "
                    "merge the two by hand"
                )
            raise clean_fs.Refused(f"{rel} changed while the capture was made; kept {kept}")
        os.fsync(dir_fd)
        return added
    finally:
        os.close(dir_fd)


def write_new(base: Path, path: Path, text: str) -> None:
    """Publish `text` at `path`, which must not exist: a temp file inside a checked directory
    descriptor, written whole and fsynced, then hard-linked to the name (refused if the name
    exists) and the directory fsynced; the temp name is removed however the call ends."""
    rel = path.relative_to(base).as_posix()
    clean_fs.read_no_link_above(path, base)
    dir_fd = clean_fs.read_bound_directory(path.parent, base)
    temp = f".{path.name}.tmp-{events.new_ulid()}"
    try:
        fd = os.open(temp, clean_fs.NEW_FILE_FLAGS, 0o644, dir_fd=dir_fd)
        try:
            clean_fs.write_whole(fd, text.encode("utf-8"))
        finally:
            os.close(fd)
        try:
            os.link(temp, path.name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd, follow_symlinks=False)
        except FileExistsError as error:
            raise clean_fs.Refused(f"{rel} exists; nothing is replaced") from error
        os.fsync(dir_fd)
    finally:
        try:
            os.unlink(temp, dir_fd=dir_fd)
        except FileNotFoundError:
            pass
        os.close(dir_fd)
