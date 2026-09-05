#!/usr/bin/env python3
"""Guarded integration of a synchronized working branch into origin/main."""

from __future__ import annotations

import atexit
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile

import yaml

from app_wrappers import refresh_app_wrappers
from asset_manager import ProjectPaths
from numbers_automation import numbers_resume_recovery


class BranchIntegrationError(RuntimeError):
    def __init__(self, message, *, recovery=None):
        super().__init__(message)
        self.recovery = recovery


APP_RUNTIME_PREFIXES = (
    "00 Master/",
    "10 Profiles/",
    "20 Templates/",
    "50 Field Guide/",
    "60 Assets/",
    "70 Canon Guides/",
    "80 Build/",
    "90 Testing/",
    "data/",
)
APP_RUNTIME_FILES = {
    "controls.md",
    "controls.yaml",
    "package.json",
    "requirements.txt",
}

CATALOG_POLICY_PATH = "00 Master/profile_catalog_policy.yaml"
CATALOG_FALLBACK_FILES = {
    CATALOG_POLICY_PATH,
    "00 Master/profile_lens_guidance.yaml",
}
CATALOG_FALLBACK_PREFIXES = ("10 Profiles/",)


def _changed_path(status_line):
    return str(status_line or "").split("\t")[-1].strip()


def _changed_paths(status_line):
    """Return both sides of a rename/copy and the single path of other changes."""
    fields = str(status_line or "").split("\t")
    return tuple(path.strip() for path in fields[1:] if path.strip())


def app_restart_required(files):
    """Return whether a running local app may retain pre-integration runtime state."""
    for item in files or ():
        path = _changed_path(item)
        if path in APP_RUNTIME_FILES or path.startswith(APP_RUNTIME_PREFIXES):
            return True
    return False


class BranchIntegrationWorkflow:
    """Prepare, review, merge, push, and resynchronize without publishing."""

    def __init__(self, root, app_refresher=None):
        self.paths = ProjectPaths(root)
        self._app_refresher = app_refresher or refresh_app_wrappers
        self._prepared = None
        self._applied = None
        self._temporary_worktrees = set()
        atexit.register(self.close)

    def _run(self, command, *, cwd=None, timeout=15 * 60):
        try:
            return subprocess.run(
                command,
                cwd=cwd or self.paths.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BranchIntegrationError(f"{Path(command[0]).name} timed out.") from exc
        except OSError as exc:
            raise BranchIntegrationError(f"Could not run {Path(command[0]).name}: {exc}") from exc

    def _require(self, label, command, *, cwd=None, timeout=15 * 60):
        completed = self._run(command, cwd=cwd, timeout=timeout)
        output = completed.stdout[-80_000:].strip()
        if completed.returncode:
            raise BranchIntegrationError(
                f"{label} failed.\n{output}",
                recovery=numbers_resume_recovery(output, "retry-with-spreadsheet-refresh"),
            )
        return {"label": label, "status": "passed", "output": output}

    def _git(self, *args, cwd=None):
        completed = self._run(["git", *args], cwd=cwd, timeout=3 * 60)
        if completed.returncode:
            raise BranchIntegrationError(completed.stdout.strip() or f"Git command failed: {' '.join(args)}")
        return completed.stdout.strip()

    def _git_ok(self, *args, cwd=None):
        return self._run(["git", *args], cwd=cwd, timeout=3 * 60).returncode == 0

    def _fetch(self):
        return self._require("Refresh origin", ["git", "fetch", "--prune", "origin"], timeout=10 * 60)

    def _branch_info(self):
        branch = self._git("branch", "--show-current")
        if not branch:
            raise BranchIntegrationError("Branch integration is unavailable on a detached Git checkout.")
        if branch == "main":
            raise BranchIntegrationError("This workspace is for integrating a working branch. The current branch is already main.")
        upstream = self._git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        expected = f"origin/{branch}"
        if upstream != expected:
            raise BranchIntegrationError(f"Branch '{branch}' must track '{expected}', not '{upstream}'.")
        return branch, upstream

    @staticmethod
    def _pending_count(value):
        try:
            pending = int(value)
        except (TypeError, ValueError) as exc:
            raise BranchIntegrationError("Pending browser draft count must be an integer.") from exc
        if pending < 0:
            raise BranchIntegrationError("Pending browser draft count cannot be negative.")
        return pending

    def _clean_status(self, cwd=None):
        return self._git("status", "--porcelain=v1", "--untracked-files=all", cwd=cwd)

    def _ahead_behind(self, left, right):
        raw = self._git("rev-list", "--left-right", "--count", f"{left}...{right}")
        left_count, right_count = raw.split()
        return int(left_count), int(right_count)

    def _remote_state(self, branch):
        branch_ref = f"origin/{branch}"
        if not self._git_ok("show-ref", "--verify", "--quiet", "refs/remotes/origin/main"):
            raise BranchIntegrationError("origin/main does not exist. Branch integration cannot determine its target.")
        if not self._git_ok("show-ref", "--verify", "--quiet", f"refs/remotes/{branch_ref}"):
            raise BranchIntegrationError(f"{branch_ref} does not exist.")
        return self._git("rev-parse", "origin/main"), self._git("rev-parse", branch_ref)

    def _catalog_boundary(self, refs, *, cwd):
        """Use canonical fallbacks plus both reviewed revisions to prevent policy evasion."""
        exact = set(CATALOG_FALLBACK_FILES)
        prefixes = set(CATALOG_FALLBACK_PREFIXES)
        for ref in refs:
            completed = self._run(
                ["git", "show", f"{ref}:{CATALOG_POLICY_PATH}"],
                cwd=cwd,
                timeout=3 * 60,
            )
            if completed.returncode:
                continue
            try:
                policy = yaml.safe_load(completed.stdout) or {}
            except yaml.YAMLError:
                continue
            sources = policy.get("protected_sources") if isinstance(policy, dict) else None
            if not isinstance(sources, dict):
                continue
            for key in ("policy", "lens_guidance"):
                path = sources.get(key)
                if isinstance(path, str) and path and not Path(path).is_absolute() and ".." not in Path(path).parts:
                    exact.add(Path(path).as_posix())
            directory = sources.get("profile_directory")
            if isinstance(directory, str) and directory and not Path(directory).is_absolute() and ".." not in Path(directory).parts:
                prefixes.add(Path(directory).as_posix().rstrip("/") + "/")
        return exact, prefixes

    def _catalog_review(self, main_ref, candidate_ref, files, *, cwd):
        exact, prefixes = self._catalog_boundary((main_ref, candidate_ref), cwd=cwd)
        protected_lines = []
        protected_paths = set()
        for line in files:
            paths = _changed_paths(line)
            matching = {
                path
                for path in paths
                if path in exact or any(path.startswith(prefix) for prefix in prefixes)
            }
            if matching:
                protected_lines.append(line)
                protected_paths.update(paths)
        diff = ""
        if protected_paths:
            diff = self._git(
                "diff",
                "--no-ext-diff",
                "--unified=3",
                f"{main_ref}..{candidate_ref}",
                "--",
                *sorted(protected_paths),
                cwd=cwd,
            )
        return {
            "catalogReviewRequired": bool(protected_lines),
            "catalogOwnerApproved": False,
            "protectedFiles": protected_lines,
            "protectedDiff": diff,
        }

    @staticmethod
    def _prepared_review_fields(prepared):
        return {
            "reviewToken": prepared["token"],
            "candidateCommit": prepared["candidateCommit"],
            "candidateTree": prepared["candidateTree"],
            "catalogReviewRequired": prepared.get("catalogReviewRequired", False),
            "catalogOwnerApproved": prepared.get("catalogOwnerApproved", False),
            "protectedFiles": list(prepared.get("protectedFiles", [])),
            "protectedDiff": prepared.get("protectedDiff", ""),
        }

    def _verify_prepared_candidate(self, prepared, *, refresh):
        if refresh:
            self._fetch()
        main_sha, branch_sha = self._remote_state(prepared["branch"])
        if main_sha != prepared["mainCommit"] or branch_sha != prepared["branchCommit"]:
            raise BranchIntegrationError("A remote branch changed after review. Prepare the integration again.")
        if self._git("rev-parse", "HEAD") != branch_sha or self._clean_status():
            raise BranchIntegrationError("The working branch changed after review. Prepare the integration again.")
        worktree = Path(prepared["worktree"])
        if not worktree.is_dir():
            raise BranchIntegrationError("The isolated integration candidate is no longer available. Prepare it again.")
        if (
            self._git("rev-parse", "HEAD", cwd=worktree) != prepared["candidateCommit"]
            or self._git("rev-parse", "HEAD^{tree}", cwd=worktree) != prepared["candidateTree"]
        ):
            raise BranchIntegrationError("The isolated integration candidate changed after review. Prepare it again.")

    def inspect(self, pending_changes=0, *, refresh=True):
        pending = self._pending_count(pending_changes)
        branch, upstream = self._branch_info()
        fetch = self._fetch() if refresh else None
        main_sha, branch_sha = self._remote_state(branch)
        head_sha = self._git("rev-parse", "HEAD")
        status = self._clean_status()
        blockers = []
        if pending:
            blockers.append(f"Resolve {pending} unsaved browser {'draft' if pending == 1 else 'drafts'} first.")
        if status:
            blockers.append("Finish Day must leave the working branch clean before integration.")
        if head_sha != branch_sha:
            ahead, behind = self._ahead_behind("HEAD", upstream)
            blockers.append(
                f"The working branch is not synchronized with {upstream} (ahead {ahead}, behind {behind}). Run Finish Day first."
            )
        branch_in_main = self._git_ok("merge-base", "--is-ancestor", branch_sha, main_sha)
        main_in_branch = self._git_ok("merge-base", "--is-ancestor", main_sha, branch_sha)
        retained = None
        if not blockers and self._applied and self._applied.get("branch") == branch:
            applied = self._applied
            if main_sha == applied["previousMain"] and branch_sha == applied["branchCommit"]:
                main_worktree = Path(applied["mainWorktree"])
                if (
                    main_worktree.is_dir()
                    and not self._clean_status(cwd=main_worktree)
                    and self._git("rev-parse", "HEAD", cwd=main_worktree) == applied["mainCommit"]
                ):
                    retained = "push-main"
            elif main_sha == applied["mainCommit"] and branch_sha == applied["branchCommit"]:
                retained = "resync"
            elif main_sha == applied["mainCommit"] and branch_sha == applied["mainCommit"]:
                retained = "complete"
        if not blockers and self._prepared and self._prepared.get("branch") == branch:
            prepared = self._prepared
            if main_sha == prepared["mainCommit"] and branch_sha == prepared["branchCommit"]:
                retained = "merge-main"
            else:
                self._remove_worktree(prepared.get("worktree"))
                self._prepared = None
        if blockers:
            phase = "blocked"
        elif retained:
            phase = retained
        elif branch_sha == main_sha:
            phase = "complete"
        elif branch_in_main:
            phase = "resync"
        else:
            phase = "review"
        commits = []
        files = []
        if phase == "review":
            commits = [line for line in self._git("log", "--format=%h %s", f"origin/main..{upstream}").splitlines() if line]
            files = [line for line in self._git("diff", "--name-status", "origin/main..." + upstream).splitlines() if line]
        elif phase == "merge-main" and self._prepared:
            commits = list(self._prepared.get("commits", []))
            files = list(self._prepared.get("files", []))
        output_parts = []
        if fetch:
            output_parts.append(fetch["output"] or "Origin refreshed.")
        output_parts.append(
            f"Working branch: {branch} ({branch_sha[:12]})\n"
            f"Target: origin/main ({main_sha[:12]})\n"
            f"Upstream: {upstream}"
        )
        result = {
            "phase": phase,
            "branch": branch,
            "upstream": upstream,
            "target": "origin/main",
            "branchCommit": branch_sha,
            "mainCommit": main_sha,
            "mainAlreadyInBranch": main_in_branch,
            "commits": commits,
            "files": files,
            "blockers": blockers,
            "recoveryActions": (
                ["open-review-build", "open-finish-day"] if blockers else []
            ),
            "output": "\n\n".join(output_parts),
        }
        if phase == "merge-main" and self._prepared:
            result.update(self._prepared_review_fields(self._prepared))
        return result

    def _add_worktree(self, start_point, *, branch=None):
        base = Path(tempfile.mkdtemp(prefix="r5-branch-integration-"))
        worktree = base / "worktree"
        command = ["git", "worktree", "add"]
        if branch is None:
            command.append("--detach")
        command.extend([str(worktree), start_point])
        try:
            self._require("Create isolated integration worktree", command, timeout=5 * 60)
        except Exception:
            shutil.rmtree(base, ignore_errors=True)
            raise
        self._temporary_worktrees.add(worktree)
        return worktree

    def _remove_worktree(self, worktree):
        if not worktree:
            return
        path = Path(worktree)
        if path in self._temporary_worktrees:
            self._run(["git", "worktree", "remove", "--force", str(path)], timeout=5 * 60)
            shutil.rmtree(path.parent, ignore_errors=True)
            self._temporary_worktrees.discard(path)

    def close(self):
        for worktree in tuple(self._temporary_worktrees):
            self._remove_worktree(worktree)

    def _restore_generated_docs(self, worktree):
        self._require("Restore generated website files", ["git", "restore", "--staged", "--worktree", "--", "docs"], cwd=worktree)
        self._require("Remove untracked generated website files", ["git", "clean", "-fd", "--", "docs"], cwd=worktree)

    @staticmethod
    def _notify(progress, stage, command="", output="", completed=False):
        if progress:
            progress(stage, command=command, output=output, completed=completed)

    def _candidate_spreadsheet_state(self, worktree):
        verification = worktree / "80 Build" / "verification_status.py"
        spreadsheets = worktree / "80 Build" / "spreadsheet_downloads.py"
        if not verification.is_file() or not spreadsheets.is_file():
            return {"refreshNeeded": False, "labels": [], "details": []}
        checks = (
            ("Verification tracker", [sys.executable, str(verification), "check"]),
            ("Matrix/settings and Setup", [sys.executable, str(spreadsheets), "all", "diagnose"]),
        )
        labels = []
        details = []
        for label, command in checks:
            completed = self._run(command, cwd=worktree, timeout=5 * 60)
            output = completed.stdout[-80_000:].strip()
            if completed.returncode == 2:
                labels.append(label)
                details.append(output or f"{label} requires refresh.")
            elif completed.returncode:
                raise BranchIntegrationError(
                    f"{label} cannot be refreshed safely.\n{output}",
                    recovery={
                        "kind": "verification-import-required",
                        "summary": "Import or resolve the verification tracker in Review & Build, complete Finish Day, then retry integration.",
                        "actions": ["open-review-build", "open-finish-day"],
                    },
                )
        return {"refreshNeeded": bool(labels), "labels": labels, "details": details}

    def prepare(
        self,
        pending_changes,
        confirmed,
        progress=None,
        allow_spreadsheet_refresh=False,
    ):
        if self._pending_count(pending_changes):
            raise BranchIntegrationError("Resolve every unsaved browser draft before preparing integration.")
        if confirmed is not True:
            raise BranchIntegrationError("Integration review confirmation is required.")
        self._notify(progress, "Refreshing and checking branches", "$ git fetch --prune origin")
        state = self.inspect(0)
        self._notify(progress, "Refreshing and checking branches", output=state.get("output", ""), completed=True)
        if state["phase"] == "blocked":
            raise BranchIntegrationError("Integration is blocked. " + " ".join(state["blockers"]))
        if state["phase"] != "review":
            return state
        self._notify(progress, "Creating isolated integration worktree", "$ git worktree add --detach <temporary> origin/main")
        worktree = self._add_worktree("origin/main")
        self._notify(progress, "Creating isolated integration worktree", output=str(worktree), completed=True)
        try:
            self._notify(
                progress,
                "Testing the branch merge",
                f"$ git merge --no-ff --no-commit {state['branchCommit'][:12]}",
            )
            merge = self._run(
                ["git", "merge", "--no-ff", "--no-commit", state["branchCommit"]],
                cwd=worktree,
                timeout=5 * 60,
            )
            if merge.returncode:
                conflicts = self._git("diff", "--name-only", "--diff-filter=U", cwd=worktree)
                self._run(["git", "merge", "--abort"], cwd=worktree)
                detail = conflicts or merge.stdout.strip()
                raise BranchIntegrationError(
                    "The working branch conflicts with current main. No branch was changed.\n" + detail
                )
            self._notify(progress, "Testing the branch merge", output=merge.stdout.strip(), completed=True)
            if self._git("diff", "--cached", "--name-only", "--", "docs", cwd=worktree):
                self._run(["git", "merge", "--abort"], cwd=worktree)
                raise BranchIntegrationError(
                    "The branch would change docs/ during integration. Regenerated website files must be handled only by publication."
                )
            steps = []
            source_command = [sys.executable, "80 Build/validator.py", "--source-only"]
            self._notify(progress, "Source validation", "$ python3 '80 Build/validator.py' --source-only")
            source_step = self._require("Source validation", source_command, cwd=worktree, timeout=15 * 60)
            steps.append(source_step)
            self._notify(progress, "Source validation", output=source_step["output"], completed=True)
            self._notify(progress, "Checking spreadsheet readiness", "$ spreadsheet readiness check")
            spreadsheet_state = self._candidate_spreadsheet_state(worktree)
            self._notify(
                progress,
                "Checking spreadsheet readiness",
                output="\n\n".join(spreadsheet_state["details"]) or "Spreadsheet-derived artifacts are current.",
                completed=True,
            )
            if spreadsheet_state["refreshNeeded"] and allow_spreadsheet_refresh is not True:
                labels = ", ".join(spreadsheet_state["labels"])
                raise BranchIntegrationError(
                    f"The isolated integration candidate requires a spreadsheet refresh: {labels}.",
                    recovery={
                        "kind": "integration-spreadsheet-refresh",
                        "summary": "Allow Profile Editor to rebuild only the stale spreadsheet-derived artifacts inside the disposable integration candidate, then continue validation. Apple Numbers runs temporarily in the background and closes automatically.",
                        "labels": spreadsheet_state["labels"],
                        "details": spreadsheet_state["details"],
                        "actions": ["retry-with-spreadsheet-refresh"],
                    },
                )
            if spreadsheet_state["refreshNeeded"]:
                refresh_command = worktree / "80 Build" / "scripts" / "build-all-spreadsheet-downloads.sh"
                self._notify(progress, "Refreshing candidate spreadsheets", "$ rebuild stale spreadsheet-derived artifacts")
                refresh = self._require(
                    "Spreadsheet refresh",
                    [str(refresh_command)],
                    cwd=worktree,
                    timeout=45 * 60,
                )
                steps.append(refresh)
                self._notify(
                    progress,
                    "Refreshing candidate spreadsheets",
                    output=refresh["output"],
                    completed=True,
                )
            for label, command, timeout in (
                ("Development build", [sys.executable, "80 Build/build.py"], 15 * 60),
                ("Full validation", [sys.executable, "80 Build/validator.py"], 15 * 60),
            ):
                display_command = "$ " + " ".join(f"'{part}'" if " " in str(part) else str(part) for part in command)
                self._notify(progress, label, display_command)
                step = self._require(label, command, cwd=worktree, timeout=timeout)
                steps.append(step)
                self._notify(progress, label, output=step["output"], completed=True)
            self._notify(progress, "Restoring generated website files", "$ git restore --staged --worktree -- docs")
            self._restore_generated_docs(worktree)
            self._notify(progress, "Restoring generated website files", completed=True)
            if self._git("status", "--porcelain=v1", "--untracked-files=all", "--", "docs", cwd=worktree):
                raise BranchIntegrationError("Generated website files could not be restored in the isolated review worktree.")
            self._notify(progress, "Creating reviewed integration candidate", f"$ git commit -m 'Merge {state['branch']} into main'")
            candidate_step = self._require(
                "Create reviewed integration candidate",
                ["git", "commit", "-m", f"Merge {state['branch']} into main"],
                cwd=worktree,
            )
            self._notify(progress, "Creating reviewed integration candidate", output=candidate_step["output"], completed=True)
            candidate = self._git("rev-parse", "HEAD", cwd=worktree)
            tree = self._git("rev-parse", "HEAD^{tree}", cwd=worktree)
            files = [line for line in self._git("diff", "--name-status", f"{state['mainCommit']}..HEAD", cwd=worktree).splitlines() if line]
            if any(line.split("\t")[-1] == "docs" or line.split("\t")[-1].startswith("docs/") for line in files):
                raise BranchIntegrationError("The reviewed integration candidate contains docs/ changes and was rejected.")
            token = secrets.token_urlsafe(24)
            catalog_review = self._catalog_review(
                state["mainCommit"],
                candidate,
                files,
                cwd=worktree,
            )
            self._prepared = {
                "token": token,
                "branch": state["branch"],
                "branchCommit": state["branchCommit"],
                "mainCommit": state["mainCommit"],
                "candidateCommit": candidate,
                "candidateTree": tree,
                "worktree": worktree,
                "commits": list(state["commits"]),
                "files": files,
                **catalog_review,
            }
            return {
                **state,
                "phase": "merge-main",
                "files": files,
                **self._prepared_review_fields(self._prepared),
                "steps": steps,
                "output": "\n\n".join(
                    f"{step['label']} — passed\n{step['output'] or '(no output)'}" for step in steps
                ),
            }
        except Exception:
            if not self._prepared or self._prepared.get("worktree") != worktree:
                self._remove_worktree(worktree)
            raise

    def approve_catalog_changes(self, review_token, confirmed):
        if confirmed is not True:
            raise BranchIntegrationError("Protected catalog owner approval requires confirmation.")
        prepared = self._prepared
        if not prepared or not secrets.compare_digest(str(review_token or ""), prepared["token"]):
            raise BranchIntegrationError("Integration review expired. Prepare and review the candidate again.")
        if not prepared.get("catalogReviewRequired"):
            raise BranchIntegrationError("This integration candidate has no protected catalog changes to approve.")
        self._verify_prepared_candidate(prepared, refresh=False)
        prepared["catalogOwnerApproved"] = True
        return {
            "phase": "merge-main",
            "branch": prepared["branch"],
            "target": "origin/main",
            "commits": list(prepared["commits"]),
            "files": list(prepared["files"]),
            **self._prepared_review_fields(prepared),
            "message": "Protected catalog changes are approved for this exact candidate. Local main is still unchanged.",
        }

    def _main_worktree(self):
        records = self._git("worktree", "list", "--porcelain").splitlines()
        path = None
        for line in records + [""]:
            if line.startswith("worktree "):
                path = Path(line.removeprefix("worktree "))
            elif line == "branch refs/heads/main" and path:
                return path, False
        return self._add_worktree("main", branch="main"), True

    def merge_main(self, review_token, confirmed):
        if confirmed is not True:
            raise BranchIntegrationError("Updating local main requires confirmation.")
        prepared = self._prepared
        if not prepared or not secrets.compare_digest(str(review_token or ""), prepared["token"]):
            raise BranchIntegrationError("Integration review expired. Prepare and review the candidate again.")
        if prepared.get("catalogReviewRequired") and not prepared.get("catalogOwnerApproved"):
            raise BranchIntegrationError(
                "Protected application catalog changes require separate owner approval before local main can change."
            )
        self._verify_prepared_candidate(prepared, refresh=True)
        main_sha = prepared["mainCommit"]
        branch_sha = prepared["branchCommit"]
        main_worktree, temporary = self._main_worktree()
        try:
            if self._clean_status(cwd=main_worktree):
                raise BranchIntegrationError(f"The main worktree has local changes and was not touched: {main_worktree}")
            if self._git("branch", "--show-current", cwd=main_worktree) != "main":
                raise BranchIntegrationError(f"The selected main worktree is not on main: {main_worktree}")
            local_main = self._git("rev-parse", "HEAD", cwd=main_worktree)
            if local_main != main_sha:
                if not self._git_ok("merge-base", "--is-ancestor", local_main, main_sha, cwd=main_worktree):
                    raise BranchIntegrationError(
                        f"Local main has history that is not a clean fast-forward to origin/main and was not changed: {main_worktree}"
                    )
                self._require(
                    "Fast-forward local main to reviewed origin/main",
                    ["git", "merge", "--ff-only", main_sha],
                    cwd=main_worktree,
                )
            self._require(
                "Merge reviewed branch into local main",
                ["git", "merge", "--no-ff", "--no-edit", prepared["branchCommit"]],
                cwd=main_worktree,
                timeout=5 * 60,
            )
            merged_commit = self._git("rev-parse", "HEAD", cwd=main_worktree)
            merged_tree = self._git("rev-parse", "HEAD^{tree}", cwd=main_worktree)
            if merged_tree != prepared["candidateTree"]:
                raise BranchIntegrationError(
                    "Local main did not produce the exact reviewed tree. Main was not pushed; inspect the local merge."
                )
            self._remove_worktree(prepared["worktree"])
            self._prepared = None
            self._applied = {
                "branch": prepared["branch"],
                "branchCommit": branch_sha,
                "previousMain": main_sha,
                "mainCommit": merged_commit,
                "mainWorktree": main_worktree,
                "temporaryMain": temporary,
                "files": list(prepared["files"]),
            }
            return {
                "phase": "push-main",
                "branch": prepared["branch"],
                "target": "origin/main",
                "mainCommit": merged_commit,
                "message": "The reviewed tree is now committed on local main. Nothing has been pushed.",
            }
        except Exception:
            if temporary and not self._applied:
                self._remove_worktree(main_worktree)
            raise

    def push_main(self, confirmed):
        if confirmed is not True:
            raise BranchIntegrationError("Pushing main requires separate confirmation.")
        applied = self._applied
        if not applied:
            raise BranchIntegrationError("No reviewed local-main integration is waiting to be pushed.")
        self._fetch()
        if self._git("rev-parse", "origin/main") != applied["previousMain"]:
            raise BranchIntegrationError("origin/main changed before push. Main was not pushed.")
        if self._clean_status(cwd=applied["mainWorktree"]):
            raise BranchIntegrationError("The main worktree changed before push. Main was not pushed.")
        if self._git("rev-parse", "HEAD", cwd=applied["mainWorktree"]) != applied["mainCommit"]:
            raise BranchIntegrationError("Local main changed before push. Main was not pushed.")
        pushed = self._require(
            "Push main",
            ["git", "push", "origin", "main:main"],
            cwd=applied["mainWorktree"],
            timeout=10 * 60,
        )
        self._fetch()
        if self._git("rev-parse", "origin/main") != applied["mainCommit"]:
            raise BranchIntegrationError("Main push completed but origin/main could not be verified.")
        return {
            "phase": "resync",
            "branch": applied["branch"],
            "target": "origin/main",
            "mainCommit": applied["mainCommit"],
            "message": "Main is synchronized. The website was not published. Resynchronize the working branch next.",
            "output": pushed["output"],
        }

    def resync_branch(self, confirmed):
        if confirmed is not True:
            raise BranchIntegrationError("Working-branch resynchronization requires confirmation.")
        branch, upstream = self._branch_info()
        self._fetch()
        main_sha, remote_branch = self._remote_state(branch)
        if self._clean_status():
            raise BranchIntegrationError("The working branch has local changes and cannot be resynchronized.")
        if self._git("rev-parse", "HEAD") != remote_branch:
            raise BranchIntegrationError(f"The working branch is not synchronized with {upstream}.")
        if not self._git_ok("merge-base", "--is-ancestor", remote_branch, main_sha):
            raise BranchIntegrationError("origin/main does not contain the working branch. Prepare integration again.")
        self._require("Fast-forward working branch to integrated main", ["git", "merge", "--ff-only", main_sha])
        pushed = self._require(
            "Push resynchronized working branch",
            ["git", "push", "origin", f"HEAD:refs/heads/{branch}"],
            timeout=10 * 60,
        )
        self._fetch()
        final = self.inspect(0, refresh=False)
        if final["phase"] != "complete":
            raise BranchIntegrationError("Branch resynchronization completed but the final state could not be verified.")
        applied = self._applied
        restart_required = app_restart_required(applied.get("files", [])) if applied else False
        if applied and applied.get("temporaryMain"):
            app_refresh = {
                "status": "unavailable",
                "rebuilt": False,
                "restartRequired": restart_required,
                "message": (
                    "Main app wrappers were not refreshed because Main used a disposable integration worktree. "
                    "Open a persistent Main project checkout and rebuild the wrappers there."
                ),
            }
            self._remove_worktree(applied["mainWorktree"])
        elif applied:
            try:
                app_refresh = self._app_refresher(Path(applied["mainWorktree"]))
            except Exception as exc:
                app_refresh = {
                    "status": "failed",
                    "rebuilt": False,
                    "message": f"Main app refresh failed: {exc}",
                }
            app_refresh["restartRequired"] = restart_required
            if restart_required:
                app_refresh["message"] = (
                    f"{app_refresh['message']} Restart any running Profile Editor and Camera Lab "
                    "to load the integrated code."
                )
        else:
            app_refresh = {
                "status": "unknown",
                "rebuilt": False,
                "restartRequired": False,
                "message": "App freshness was not recorded for this previously completed integration.",
            }
        self._applied = None
        final.update(
            {
                "message": (
                    "Integration complete. Main and the working branch are synchronized; "
                    "the website was not published."
                ),
                "output": pushed["output"],
                "appRefresh": app_refresh,
            }
        )
        return final
