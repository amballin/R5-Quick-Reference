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

local_workspace_dir() {
    if [[ -z "${PRS_LOCAL_WORKSPACE:-}" ]]; then
        printf '%s Local\n' "$PROJECT_ROOT"
        return
    fi

    case "$PRS_LOCAL_WORKSPACE" in
        "~") printf '%s\n' "$HOME" ;;
        "~/"*) printf '%s/%s\n' "$HOME" "${PRS_LOCAL_WORKSPACE#~/}" ;;
        /*) printf '%s\n' "$PRS_LOCAL_WORKSPACE" ;;
        *) printf '%s/%s\n' "$PROJECT_ROOT" "$PRS_LOCAL_WORKSPACE" ;;
    esac
}

clean_generated_metadata() {
    local workspace root
    workspace="$(local_workspace_dir)"

    for root in "$PROJECT_ROOT/docs" "$workspace/Build Output"; do
        if [[ -d "$root" ]]; then
            find "$root" -type f -name ".DS_Store" -delete || return 1
        fi
    done
}

prepare_development_docs_for_handoff() {
    if [[ -z "$(git status --porcelain -- docs)" ]]; then
        return 0
    fi

    echo
    echo "PAGES SEPARATION: docs/ contains generated changes."
    echo "GitHub Pages serves main/docs, so a source-handoff commit must leave docs/ unchanged."
    echo "finish-day can back up these files locally, restore docs/ to HEAD, and continue with source changes."
    echo "Use publish.sh separately only when you intentionally want to update the live site."
    echo
    if ! ask_yes_no "Back up and restore docs/ now so this handoff does not publish?"; then
        echo "Handoff postponed. No docs/ files were changed by finish-day."
        return 1
    fi

    local workspace backup_root backup_dir timestamp
    workspace="$(local_workspace_dir)"
    backup_root="$workspace/Backups"
    timestamp="$(date '+%Y%m%d-%H%M%S')"
    backup_dir="$backup_root/$timestamp-finish-day-docs"

    mkdir -p "$backup_dir" || return 1
    tar -czf "$backup_dir/docs-working-tree.tar.gz" docs || return 1
    git status --short --untracked-files=all -- docs > "$backup_dir/git-status.txt" || return 1
    git diff --binary -- docs > "$backup_dir/unstaged.patch" || return 1
    git diff --cached --binary -- docs > "$backup_dir/staged.patch" || return 1
    tar -tzf "$backup_dir/docs-working-tree.tar.gz" > /dev/null || return 1

    git restore --staged --worktree -- docs || return 1
    git clean -fd -- docs || return 1

    if [[ -n "$(git status --porcelain -- docs)" ]]; then
        echo "PAGES SAFETY BLOCK: docs/ could not be restored completely."
        echo "Recovery backup: $backup_dir"
        return 1
    fi

    echo "Development docs/ changes were backed up and excluded from the handoff commit."
    echo "Recovery backup: $backup_dir"
    return 0
}

assert_no_worktree_pages_changes() {
    if [[ -z "$(git status --porcelain -- docs)" ]]; then
        return 0
    fi

    echo
    echo "PAGES SAFETY BLOCK: docs/ changed unexpectedly after handoff preparation."
    echo "Nothing will be committed or pushed."
    return 1
}

block_outgoing_pages_changes() {
    if git diff --quiet '@{upstream}..HEAD' -- docs; then
        return 0
    fi

    echo
    echo "PAGES SAFETY BLOCK: Unpushed commits contain docs/ changes."
    echo "Pushing them can update the live GitHub Pages site."
    echo "finish-day will not push a Pages-changing commit."
    echo "Review the commits manually; intentional publication must use the authorized publish workflow."
    return 1
}

echo "Photography Reference System — Finished-for-Today Check"
echo

clean_generated_metadata || {
    echo "Could not remove Finder metadata from generated output. Nothing was committed or pushed."
    exit 1
}

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
        clean_generated_metadata || {
            echo "Could not remove Finder metadata from generated output. Nothing was committed or pushed."
            exit 1
        }
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
        python3 "80 Build/validator.py" || {
            echo
            echo "Post-build validation failed. Nothing was committed or pushed."
            exit 1
        }
        echo
        echo "Pre-build validation, normal development build, and post-build validation completed."
        echo "A normal build may refresh docs/. finish-day will separate those files before staging source changes."
    else
        echo
        echo "Validation/build postponed."
    fi

    echo
    echo "Current changes:"
    git status --short
    echo
    prepare_development_docs_for_handoff || exit 1
    echo
    echo "Source changes eligible for the handoff commit:"
    git status --short
    echo
    if ask_yes_no "Stage every change listed above for one intentional commit?"; then
        git add -A || exit 1
        assert_no_worktree_pages_changes || exit 1
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
    block_outgoing_pages_changes || exit 1
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
