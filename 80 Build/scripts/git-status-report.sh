#!/usr/bin/env bash

set -u

EXPECTED_BRANCH="${PRS_EXPECTED_BRANCH:-main}"
REMOTE_NAME="${PRS_REMOTE_NAME:-origin}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

readonly EXIT_LOCAL_CHANGES=10
readonly EXIT_AHEAD=20
readonly EXIT_BEHIND=30
readonly EXIT_DIVERGED=40
readonly EXIT_WRONG_BRANCH=50
readonly EXIT_NO_UPSTREAM=51
readonly EXIT_FETCH_FAILED=52
readonly EXIT_NOT_REPOSITORY=53

cd "$PROJECT_ROOT" || {
    echo "ERROR: Cannot access the project root: $PROJECT_ROOT" >&2
    exit "$EXIT_NOT_REPOSITORY"
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: $PROJECT_ROOT is not a Git working tree." >&2
    exit "$EXIT_NOT_REPOSITORY"
fi

CURRENT_BRANCH="$(git branch --show-current)"
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"

echo "Photography Reference System — Git Status"
echo
echo "Project:  $PROJECT_ROOT"
echo "Branch:   ${CURRENT_BRANCH:-detached HEAD}"
echo "Expected: $EXPECTED_BRANCH"
echo "Upstream: ${UPSTREAM:-none}"
echo

if [[ "$CURRENT_BRANCH" != "$EXPECTED_BRANCH" ]]; then
    echo "STATUS: WRONG BRANCH"
    echo "Expected '$EXPECTED_BRANCH' but found '${CURRENT_BRANCH:-detached HEAD}'."
    echo "Do not switch branches automatically. Obtain project-owner approval first."
    exit "$EXIT_WRONG_BRANCH"
fi

if [[ -z "$UPSTREAM" ]]; then
    echo "STATUS: NO UPSTREAM"
    echo "The current branch has no configured upstream branch."
    echo "Review the branch and remote configuration before building or syncing."
    exit "$EXIT_NO_UPSTREAM"
fi

if [[ "$UPSTREAM" != "$REMOTE_NAME/"* ]]; then
    echo "STATUS: UNEXPECTED UPSTREAM"
    echo "Expected an upstream on '$REMOTE_NAME', but found '$UPSTREAM'."
    echo "Review the branch and remote configuration before building or syncing."
    exit "$EXIT_NO_UPSTREAM"
fi

echo "Fetching $REMOTE_NAME with pruning..."
if ! git fetch --prune "$REMOTE_NAME"; then
    echo
    echo "STATUS: FETCH FAILED"
    echo "Remote state could not be refreshed, so synchronization cannot be confirmed."
    echo "Check the network and remote access, then run this report again."
    exit "$EXIT_FETCH_FAILED"
fi

AHEAD="$(git rev-list --count "$UPSTREAM"..HEAD)"
BEHIND="$(git rev-list --count HEAD.."$UPSTREAM")"
WORKTREE_STATUS="$(git status --short)"

echo
echo "Remote comparison:"
echo "  Ahead:  $AHEAD commit(s)"
echo "  Behind: $BEHIND commit(s)"
echo
echo "Working tree:"
if [[ -n "$WORKTREE_STATUS" ]]; then
    printf '%s\n' "$WORKTREE_STATUS"
else
    echo "  clean"
fi
echo

if (( AHEAD > 0 && BEHIND > 0 )); then
    echo "STATUS: DIVERGED"
    echo "Local and remote both contain unique commits."
    echo "Do not pull, push, merge, or build until the histories are reviewed manually."
    exit "$EXIT_DIVERGED"
fi

if (( BEHIND > 0 )); then
    echo "STATUS: BEHIND"
    echo "The remote contains newer commits."
    if [[ -n "$WORKTREE_STATUS" ]]; then
        echo "Local changes also exist; preserve and review them before attempting a pull."
    else
        echo "Recommended next action: git pull --ff-only"
    fi
    exit "$EXIT_BEHIND"
fi

if (( AHEAD > 0 )); then
    echo "STATUS: AHEAD"
    echo "Local commits have not been pushed to $UPSTREAM."
    if [[ -n "$WORKTREE_STATUS" ]]; then
        echo "Uncommitted or untracked local changes also remain."
    fi
    echo "Review the listed state, then push only with explicit approval."
    exit "$EXIT_AHEAD"
fi

if [[ -n "$WORKTREE_STATUS" ]]; then
    echo "STATUS: LOCAL CHANGES"
    echo "Tracked modifications and/or untracked files remain locally."
    echo "Review, validate, build if appropriate, and commit intentionally before switching Macs."
    exit "$EXIT_LOCAL_CHANGES"
fi

echo "STATUS: CLEAN AND SYNCHRONIZED"
echo "The working tree is clean and local HEAD matches $UPSTREAM."
exit 0
