#!/bin/sh
# HANDOFF-0049 Part B: move KGME into one home, ~/Projects/KGME/ (brain/, design/, work/).
#
# Michou runs this himself, from his home directory, with no Claude Code, Codex, Obsidian or
# VS Code session open in the repository:
#     cd ~ && sh ~/Projects/Automate/control/move-home.sh
# `--check` runs every precondition below and stops before the first move.
# It prints each step before doing it and stops at the first failure. It moves with `mv` and
# `git worktree repair` only; the one deletion is the brain's `.venv`, which holds absolute
# paths and is rebuilt by `uv sync --frozen`. Reversal: move the two folders back and run
# `git -C ~/Projects/Automate worktree repair ~/Projects/Automate-design`.
set -eu

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

OLD="$HOME/Projects/Automate"
OLD_DESIGN="$HOME/Projects/Automate-design"
KGME="$HOME/Projects/KGME"
BRAIN="$KGME/brain"
DESIGN="$KGME/design"
WORK="$KGME/work"

step() {
    printf '\n==> %s\n' "$1"
}

refuse() {
    printf '\nmove-home: refused: %s\n' "$1" >&2
    exit 1
}

step "Check the starting point"
[ -d "$OLD/.git" ] || refuse "$OLD is not the repository (already moved?)"
[ ! -e "$BRAIN" ] || refuse "$BRAIN already exists"
[ ! -e "$DESIGN" ] || refuse "$DESIGN already exists"
case "$PWD/" in
    "$OLD"/* | "$OLD_DESIGN"/*) refuse "run this from outside the repository: cd ~ first" ;;
esac
branch=$(git -C "$OLD" rev-parse --abbrev-ref HEAD)
[ "$branch" = "main" ] || refuse "$OLD is on branch $branch, not main"
echo "repository: $OLD (main)"
[ -d "$OLD_DESIGN" ] && echo "design worktree: $OLD_DESIGN" || echo "design worktree: none"

step "Refuse while a claude or codex process works inside the repository"
# Enumeration must succeed to count as idle: pgrep exits 1 for "none" and higher for a
# failure; a working directory that cannot be read is a refusal, never a pass (F2).
set +e
pids=$(pgrep -f 'claude|codex')
code=$?
set -e
case "$code" in
    0) ;;
    1) pids="" ;;
    *) refuse "could not list claude or codex processes (pgrep exit $code)" ;;
esac
for pid in $pids; do
    set +e
    cwd=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null)
    code=$?
    set -e
    [ "$code" -eq 0 ] || refuse "could not read the working directory of process $pid (lsof exit $code); retry once it has exited"
    dir=$(printf '%s\n' "$cwd" | sed -n 's/^n//p')
    case "$dir/" in
        "$OLD"/* | "$OLD_DESIGN"/*) refuse "process $pid has its working directory in $dir" ;;
    esac
done
echo "no claude or codex process works inside the repository"

if [ "$CHECK_ONLY" -eq 1 ]; then
    printf '\n==> check only: every precondition holds; nothing was moved\n'
    exit 0
fi

step "Create $KGME and $WORK"
mkdir -p "$KGME" "$WORK"

step "Move $OLD to $BRAIN"
mv "$OLD" "$BRAIN"

if [ -d "$OLD_DESIGN" ]; then
    step "Move $OLD_DESIGN to $DESIGN"
    mv "$OLD_DESIGN" "$DESIGN"
    step "Repair the worktree links in both directions"
    git -C "$BRAIN" worktree repair "$DESIGN"
fi

step "Rebuild the brain's .venv, which holds the old absolute path"
rm -r "$BRAIN/.venv"
(cd "$BRAIN" && uv sync --frozen)

step "Check the git hook path"
hooks=$(git -C "$BRAIN" config --get core.hooksPath || true)
[ "$hooks" = "control/git-hooks" ] || refuse "core.hooksPath is '$hooks'; run: make -C $BRAIN setup"
echo "core.hooksPath = $hooks"

step "make check in the brain"
make -C "$BRAIN" check

step "Worktrees (expect brain on main and design on design)"
git -C "$BRAIN" worktree list

cat <<EOF

==> Done. By hand, then the checks of HANDOFF-0049 Part B section 5:
  1. ~/.zshrc: KGME_HOME=$BRAIN, and the kgh and kgq functions; then open a new terminal.
  2. ~/.codex/kgme.config.toml: the writable root becomes $BRAIN.
  3. Warp: the new-tab folder becomes $BRAIN.
  4. Obsidian: skip; HANDOFF-0051 sets the vault.
  5. VS Code: open $BRAIN.
  6. Cowork: add the folder $KGME, the whole home.
  7. The design worktree's own .venv, if it has one, is rebuilt with: (cd $DESIGN && uv sync --frozen)
Checks: 'git -C $BRAIN worktree list' shows both; 'kgh' lands in brain/; a test commit
pushes; a ledger event lands; Backblaze's selection still covers ~/Projects. Claude Code's
past sessions stay listed under the old path and still resume by id.
EOF
