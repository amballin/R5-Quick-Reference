#!/usr/bin/env python3
"""Shared guarded Finish Day workflow for the CLI and Profile Editor."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tarfile

from asset_manager import ProjectPaths
from numbers_automation import numbers_resume_recovery


class FinishDayError(RuntimeError):
    def __init__(self, message, *, recovery=None):
        super().__init__(message)
        self.recovery = recovery


class FinishDayWorkflow:
    STATUS_BLOCKED = {30, 40, 50, 51, 52, 53}

    def __init__(self, root):
        self.paths = ProjectPaths(root)
        self._prepared = None

    def _run(self, command, *, timeout=15 * 60, env=None):
        try:
            return subprocess.run(
                command,
                cwd=self.paths.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise FinishDayError(f"{Path(command[0]).name} timed out.") from exc
        except OSError as exc:
            raise FinishDayError(f"Could not run {Path(command[0]).name}: {exc}") from exc

    def _require_success(self, label, command, *, timeout=15 * 60, env=None):
        completed = self._run(command, timeout=timeout, env=env)
        output = completed.stdout[-80_000:].strip()
        if completed.returncode:
            raise FinishDayError(
                f"{label} failed.\n{output}",
                recovery=numbers_resume_recovery(output, "resume-finish-day"),
            )
        return {"label": label, "status": "passed", "output": output}

    def _status_report(self):
        script = self.paths.root / "80 Build" / "scripts" / "git-status-report.sh"
        env = dict(os.environ, PRS_SUPPRESS_GENERATED_DOC_DETAILS="1")
        completed = self._run([str(script)], timeout=3 * 60, env=env)
        return completed.returncode, completed.stdout[-80_000:].strip()

    def _git_text(self, *args):
        completed = self._run(["git", *args], timeout=3 * 60)
        if completed.returncode:
            raise FinishDayError(completed.stdout.strip() or f"Git command failed: {' '.join(args)}")
        return completed.stdout.strip()

    def _worktree_status(self, *, include_docs=True):
        command = ["status", "--porcelain=v1", "--untracked-files=all", "--", "."]
        if not include_docs:
            command.append(":(exclude)docs")
        return self._git_text(*command)

    def _source_snapshot(self):
        digest = hashlib.sha256()
        diff = self._git_text("diff", "--binary", "HEAD", "--", ".", ":(exclude)docs")
        digest.update(diff.encode("utf-8"))
        untracked = self._git_text("ls-files", "--others", "--exclude-standard", "--", ".", ":(exclude)docs")
        for relative in sorted(line for line in untracked.splitlines() if line):
            path = self.paths.root / relative
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def _branch_info(self):
        branch = self._git_text("branch", "--show-current")
        if not branch:
            raise FinishDayError("Finish Day is unavailable on a detached Git checkout.")
        upstream = self._git_text("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        expected = f"origin/{branch}"
        if upstream != expected:
            raise FinishDayError(f"Branch '{branch}' must track '{expected}', not '{upstream}'.")
        return branch, upstream

    @staticmethod
    def _pending_count(value):
        try:
            pending = int(value)
        except (TypeError, ValueError) as exc:
            raise FinishDayError("Pending browser draft count must be an integer.") from exc
        if pending < 0:
            raise FinishDayError("Pending browser draft count cannot be negative.")
        return pending

    def inspect(self, pending_changes=0):
        pending = self._pending_count(pending_changes)
        branch, upstream = self._branch_info()
        status_code, status_output = self._status_report()
        verification = self._run(
            [sys.executable, "80 Build/verification_status.py", "check"], timeout=5 * 60
        )
        verification_output = verification.stdout[-80_000:].strip()
        spreadsheet_state = self._spreadsheet_state(verification)
        source_status = self._worktree_status(include_docs=False)
        all_status = self._worktree_status(include_docs=True)
        source_files = [line for line in source_status.splitlines() if line.strip()]
        has_docs = bool(self._git_text("status", "--porcelain=v1", "--untracked-files=all", "--", "docs"))
        blockers = []
        if pending:
            blockers.append(f"Resolve {pending} unsaved browser {'draft' if pending == 1 else 'drafts'} before Finish Day.")
        if verification.returncode not in {0, 2}:
            blockers.append(
                verification_output
                or "The verification tracker is not current and synchronized."
            )
        if spreadsheet_state["status"] == "blocked":
            blockers.extend(spreadsheet_state["details"])
        if status_code in self.STATUS_BLOCKED or status_code not in {0, 10, 20}:
            blockers.append("Repository synchronization safety did not pass. Review the status details.")
        recovery_actions = []
        if pending:
            recovery_actions.append("open-review-build")
        if verification.returncode not in {0, 2}:
            recovery_actions.append("import-verification-tracker")
        if status_code in self.STATUS_BLOCKED:
            recovery_actions.append("show-status-details")
        ahead = status_code == 20
        if blockers:
            phase = "blocked"
        elif source_files or has_docs:
            phase = "prepare"
        elif ahead:
            phase = "push"
        elif status_code == 0 and not all_status:
            phase = "complete"
        else:
            phase = "prepare"
        return {
            "phase": phase,
            "branch": branch,
            "upstream": upstream,
            "pendingChanges": pending,
            "sourceFiles": source_files,
            "generatedDocsChanged": has_docs,
            "spreadsheetState": spreadsheet_state,
            "recoveryActions": list(dict.fromkeys(recovery_actions)),
            "blockers": blockers,
            "statusCode": status_code,
            "output": "\n\n".join(part for part in (status_output, verification_output) if part),
        }

    def _spreadsheet_state(self, verification=None):
        verification = verification or self._run(
            [sys.executable, "80 Build/verification_status.py", "check"], timeout=5 * 60
        )
        labels = []
        details = []
        if verification.returncode == 2:
            labels.append("Verification tracker")
            details.append(verification.stdout[-80_000:].strip())
        spreadsheet_script = self.paths.root / "80 Build" / "spreadsheet_downloads.py"
        if spreadsheet_script.is_file():
            spreadsheets = self._run(
                [sys.executable, str(spreadsheet_script), "all", "diagnose"], timeout=5 * 60
            )
            output = spreadsheets.stdout[-80_000:].strip()
            if spreadsheets.returncode == 2:
                labels.append("Matrix/settings and Setup")
                details.append(output)
            elif spreadsheets.returncode:
                return {
                    "status": "blocked",
                    "refreshNeeded": False,
                    "labels": [],
                    "details": [output or "Spreadsheet readiness could not be determined."],
                }
        status = "refresh-needed" if labels else "current"
        return {"status": status, "refreshNeeded": bool(labels), "labels": labels, "details": details}

    def _clean_generated_metadata(self):
        for root in (self.paths.pages_output_dir, self.paths.output_dir):
            if not root.is_dir():
                continue
            for path in root.rglob(".DS_Store"):
                path.unlink()

    def _verification_check(self):
        return self._require_success(
            "Verification status",
            [sys.executable, "80 Build/verification_status.py", "check"],
            timeout=5 * 60,
        )

    @staticmethod
    def _notify(progress, stage, command="", output="", completed=False):
        if progress:
            progress(stage, command=command, output=output, completed=completed)

    def _backup_and_restore_docs(self):
        docs_status = self._git_text("status", "--porcelain=v1", "--untracked-files=all", "--", "docs")
        if not docs_status:
            return None
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = self.paths.backups_dir / f"{timestamp}-finish-day-docs"
        backup_dir.mkdir(parents=True, exist_ok=False)
        archive = backup_dir / "docs-working-tree.tar.gz"
        with tarfile.open(archive, "w:gz") as bundle:
            bundle.add(self.paths.pages_output_dir, arcname="docs")
        (backup_dir / "git-status.txt").write_text(docs_status + "\n", encoding="utf-8")
        (backup_dir / "unstaged.patch").write_text(
            self._git_text("diff", "--binary", "--", "docs") + "\n", encoding="utf-8"
        )
        (backup_dir / "staged.patch").write_text(
            self._git_text("diff", "--cached", "--binary", "--", "docs") + "\n", encoding="utf-8"
        )
        with tarfile.open(archive, "r:gz") as bundle:
            if not bundle.getmembers():
                raise FinishDayError(f"Generated-docs recovery archive is empty: {archive}")
        self._require_success("Restore tracked generated docs", ["git", "restore", "--staged", "--worktree", "--", "docs"])
        self._require_success("Remove archived untracked generated docs", ["git", "clean", "-fd", "--", "docs"])
        if self._git_text("status", "--porcelain=v1", "--untracked-files=all", "--", "docs"):
            raise FinishDayError(f"Generated docs could not be restored completely. Recovery backup: {backup_dir}")
        return str(backup_dir)

    def prepare(
        self,
        pending_changes,
        confirmed,
        progress=None,
        allow_spreadsheet_refresh=False,
    ):
        pending = self._pending_count(pending_changes)
        if pending:
            raise FinishDayError(f"Resolve {pending} unsaved browser drafts before preparing Finish Day.")
        if confirmed is not True:
            raise FinishDayError("Finish Day preparation confirmation is required.")
        self._notify(
            progress,
            "Checking Finish Day readiness",
            "$ ./80 Build/scripts/git-status-report.sh",
        )
        initial = self.inspect(0)
        self._notify(progress, "Checking Finish Day readiness", completed=True)
        if initial["phase"] == "blocked":
            raise FinishDayError("Finish Day is blocked. " + " ".join(initial["blockers"]))
        if initial["phase"] in {"complete", "push"}:
            return initial
        self._notify(progress, "Cleaning disposable build metadata", "Remove recognized .DS_Store files from generated output")
        self._clean_generated_metadata()
        self._notify(progress, "Cleaning disposable build metadata", completed=True)
        steps = []
        self._notify(progress, "Source validation", "$ python3 '80 Build/validator.py' --source-only")
        source = self._require_success(
            "Source validation", [sys.executable, "80 Build/validator.py", "--source-only"], timeout=15 * 60
        )
        steps.append(source)
        self._notify(progress, "Source validation", output=source["output"], completed=True)
        spreadsheet_state = initial.get("spreadsheetState") or {}
        if spreadsheet_state.get("refreshNeeded") and allow_spreadsheet_refresh is not True:
            raise FinishDayError(
                "Finish Day requires a spreadsheet refresh before the development build.",
                recovery={
                    "kind": "finish-day-spreadsheet-refresh",
                    "summary": "Allow Profile Editor to rebuild only the stale spreadsheet-derived artifacts, then continue Finish Day. Apple Numbers runs temporarily in the background and closes automatically.",
                    "details": spreadsheet_state.get("details") or [],
                    "actions": ["retry-with-spreadsheet-refresh"],
                },
            )
        if spreadsheet_state.get("refreshNeeded"):
            refresh_command = self.paths.root / "80 Build" / "scripts" / "build-all-spreadsheet-downloads.sh"
            self._notify(progress, "Refreshing spreadsheets", "$ rebuild stale spreadsheet-derived artifacts")
            refresh = self._require_success(
                "Spreadsheet refresh",
                [str(refresh_command)],
                timeout=45 * 60,
            )
            steps.append(refresh)
            self._notify(progress, "Refreshing spreadsheets", output=refresh["output"], completed=True)
        self._notify(progress, "Checking verification status", "$ check verification status")
        verification = self._verification_check()
        steps.append(verification)
        self._notify(progress, "Checking verification status", output=verification["output"], completed=True)
        for label, command, timeout in (
            ("Development build", [sys.executable, "80 Build/build.py"], 15 * 60),
            ("Full validation", [sys.executable, "80 Build/validator.py"], 15 * 60),
        ):
            display_command = "$ " + " ".join(f"'{part}'" if " " in str(part) else str(part) for part in command)
            self._notify(progress, label, display_command)
            step = self._require_success(label, command, timeout=timeout)
            steps.append(step)
            self._notify(progress, label, output=step["output"], completed=True)
        self._notify(progress, "Protecting generated website files", "Back up and restore generated docs/")
        backup = self._backup_and_restore_docs()
        self._notify(
            progress,
            "Protecting generated website files",
            output=f"Recovery backup: {backup}" if backup else "Generated docs/ did not require restoration.",
            completed=True,
        )
        source_status = self._worktree_status(include_docs=False)
        source_files = [line for line in source_status.splitlines() if line.strip()]
        if not source_files:
            result = self.inspect(0)
            result.update({"steps": steps, "docsBackup": backup})
            return result
        token = secrets.token_urlsafe(24)
        self._prepared = {"token": token, "snapshot": self._source_snapshot()}
        return {
            "phase": "commit",
            "branch": initial["branch"],
            "upstream": initial["upstream"],
            "sourceFiles": source_files,
            "reviewToken": token,
            "steps": steps,
            "docsBackup": backup,
            "output": "\n\n".join(
                f"{step['label']} — {step['status']}\n{step['output'] or '(no output)'}" for step in steps
            ),
        }

    def commit(self, review_token, message, confirmed):
        if confirmed is not True:
            raise FinishDayError("Commit confirmation is required.")
        if not self._prepared or not secrets.compare_digest(str(review_token or ""), self._prepared["token"]):
            raise FinishDayError("Finish Day review expired. Prepare and review the file list again.")
        commit_message = " ".join(str(message or "").split())
        if not commit_message:
            raise FinishDayError("A non-empty commit message is required.")
        if len(commit_message) > 200:
            raise FinishDayError("Commit message must be 200 characters or fewer.")
        if self._source_snapshot() != self._prepared["snapshot"]:
            self._prepared = None
            raise FinishDayError("Source changed after Finish Day review. Prepare and review the file list again.")
        if self._git_text("status", "--porcelain=v1", "--untracked-files=all", "--", "docs"):
            self._prepared = None
            raise FinishDayError("Generated docs changed after preparation. Nothing was committed.")
        self._require_success("Stage reviewed source", ["git", "add", "-A"])
        if self._git_text("status", "--porcelain=v1", "--untracked-files=all", "--", "docs"):
            raise FinishDayError("Generated docs entered the staged change. Nothing was committed.")
        stat = self._git_text("diff", "--cached", "--stat")
        self._require_success("Commit reviewed source", ["git", "commit", "-m", commit_message])
        self._prepared = None
        status = self.inspect(0)
        status.update({"commitStat": stat, "message": commit_message})
        return status

    def push(self, confirmed):
        if confirmed is not True:
            raise FinishDayError("Push confirmation is required.")
        self._verification_check()
        branch, upstream = self._branch_info()
        status_code, status_output = self._status_report()
        if status_code != 20:
            raise FinishDayError("Push is available only when the current branch is ahead of its matching upstream.\n" + status_output)
        pages_diff = self._run(["git", "diff", "--quiet", "@{upstream}..HEAD", "--", "docs"], timeout=3 * 60)
        if pages_diff.returncode != 0:
            raise FinishDayError("Unpushed commits contain docs/ changes. Finish Day will not push a Pages-changing commit.")
        pushed = self._require_success("Push current branch", ["git", "push"], timeout=10 * 60)
        final_code, final_output = self._status_report()
        if final_code != 0:
            raise FinishDayError("Push completed but final synchronization could not be confirmed.\n" + final_output)
        return {
            "phase": "complete",
            "branch": branch,
            "upstream": upstream,
            "output": f"{pushed['output']}\n\n{final_output}".strip(),
            "message": "FINISHED FOR TODAY: Safe to switch Macs.",
        }


def ask_yes_no(prompt):
    return input(f"{prompt} [y/N] ").strip().casefold() == "y"


def run_interactive(root):
    workflow = FinishDayWorkflow(root)
    print("Photography Reference System — Finished-for-Today Check\n")
    status = workflow.inspect(0)
    print(status["output"])
    if status["phase"] == "blocked":
        print("\nNOT FINISHED: " + " ".join(status["blockers"]))
        return 1
    if status["phase"] == "complete":
        print("\nFINISHED FOR TODAY: Safe to switch Macs.")
        return 0
    if status["phase"] == "prepare":
        allow_spreadsheet_refresh = False
        spreadsheet_state = status.get("spreadsheetState") or {}
        if spreadsheet_state.get("refreshNeeded"):
            print("\nSpreadsheet refresh required: " + ", ".join(spreadsheet_state.get("labels") or []))
            allow_spreadsheet_refresh = ask_yes_no(
                "Rebuild only the stale spreadsheet-derived artifacts now? Apple Numbers runs temporarily in the background and closes automatically"
            )
            if not allow_spreadsheet_refresh:
                print("Preparation postponed. No spreadsheet, commit, or push action was performed.")
                return 1
        if not ask_yes_no("Run validation/build and safely separate generated docs now?"):
            print("Preparation postponed. Nothing was committed or pushed.")
            return 1
        status = workflow.prepare(
            0, True, allow_spreadsheet_refresh=allow_spreadsheet_refresh
        )
        if status.get("output"):
            print("\n" + status["output"])
    if status["phase"] == "commit":
        print("\nSource changes eligible for the handoff commit:")
        print("\n".join(status["sourceFiles"]))
        if not ask_yes_no("Commit exactly these source changes?"):
            print("Commit postponed. No commit or push was performed.")
            return 1
        message = input("Commit message: ").strip()
        status = workflow.commit(status["reviewToken"], message, True)
    if status["phase"] == "push":
        if not ask_yes_no(f"Push {status['branch']} to {status['upstream']} now?"):
            print("Push postponed. Do not switch Macs yet.")
            return 1
        status = workflow.push(True)
    print("\n" + status.get("message", "FINISHED FOR TODAY: Safe to switch Macs."))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the guarded Finish Day workflow.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        return run_interactive(args.root.resolve())
    except FinishDayError as exc:
        print(f"\nNOT FINISHED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
