#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
STATUS_SCRIPT="$SCRIPT_DIR/git-status-report.sh"

cd "$PROJECT_ROOT" || exit 1

ask_yes_no() {
    local prompt="$1"
    local reply
    read -r -p "$prompt [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

run_status() {
    "$STATUS_SCRIPT"
    return $?
}

echo "Photography Reference System — Finished-for-Today Check"
echo

run_status
RESULT=$?

case "$RESULT" in
    0)
        echo
        echo "FINISHED FOR TODAY: Safe to switch Macs."
        exit 0
        ;;
    30)
        echo
        echo "NOT FINISHED: The remote contains newer work."
        echo "No pull was attempted. If the working tree is clean, the safe update command is:"
        echo "  git pull --ff-only"
        exit 1
        ;;
    40)
        echo
        echo "NOT FINISHED: Histories have diverged and require manual review."
        exit 1
        ;;
    50|51|52|53)
        echo
        echo "NOT FINISHED: Repository safety could not be confirmed."
        exit 1
        ;;
esac

if [[ -n "$(git status --porcelain)" ]]; then
    echo
    if ask_yes_no "Run the documented validator and normal development build now?"; then
        echo
        python3 "80 Build/validator.py" || {
            echo
            echo "Validation failed. Nothing was committed or pushed."
            exit 1
        }
        python3 "80 Build/build.py" || {
            echo
            echo "Build failed. Nothing was committed or pushed."
            exit 1
        }
        echo
        echo "Validation and normal development build completed."
        echo "Review generated docs changes carefully; a computer handoff is not a publication."
    else
        echo
        echo "Validation/build postponed."
    fi

    echo
    echo "Current changes:"
    git status --short
    echo
    if ask_yes_no "Stage every change listed above for one intentional commit?"; then
        git add -A || exit 1
        echo
        git diff --cached --stat
        echo
        if ask_yes_no "Commit exactly these staged changes?"; then
            read -r -p "Commit message: " COMMIT_MESSAGE
            if [[ -z "$COMMIT_MESSAGE" ]]; then
                echo "Commit cancelled: a non-empty message is required."
                exit 1
            fi
            git commit -m "$COMMIT_MESSAGE" || exit 1
        else
            echo "Commit postponed. Staged changes remain; review them before continuing."
            exit 1
        fi
    else
        echo "Commit postponed. Local changes remain."
        exit 1
    fi
fi

echo
run_status
RESULT=$?

if [[ "$RESULT" -eq 20 ]]; then
    echo
    if ask_yes_no "Push the current branch to its configured upstream now?"; then
        git push || {
            echo "Push failed. The repository is not synchronized."
            exit 1
        }
    else
        echo "Push postponed. Do not switch Macs yet."
        exit 1
    fi
elif [[ "$RESULT" -ne 0 ]]; then
    echo
    echo "NOT FINISHED: The repository state changed and requires review."
    exit 1
fi

echo
echo "Final verification:"
run_status
RESULT=$?

if [[ "$RESULT" -eq 0 ]]; then
    echo
    echo "FINISHED FOR TODAY: Safe to switch Macs."
    exit 0
fi

echo
echo "NOT FINISHED: The final clean-and-synchronized check did not pass."
exit 1
