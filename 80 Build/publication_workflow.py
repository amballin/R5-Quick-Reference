#!/usr/bin/env python3
"""Guarded Profile Editor workflow around the supported website publisher."""

from __future__ import annotations

from datetime import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys

import yaml

from asset_manager import ProjectPaths
from numbers_automation import numbers_resume_recovery
from release_notes import load_release_notes
from spreadsheet_revisions import spreadsheet_build_id


class PublicationWorkflowError(RuntimeError):
    def __init__(self, message, *, recovery=None):
        super().__init__(message)
        self.recovery = recovery


class PublicationWorkflow:
    SPREADSHEET_MODES = {"automatic", "force", "remove", "preserve", "replace"}

    def __init__(self, root):
        self.paths = ProjectPaths(root)
        self.metadata_path = self.paths.root / "80 Build" / "publish_metadata.yaml"
        self.notes_path = self.paths.root / "00 Master" / "release_notes.yaml"
        self.publisher = self.paths.root / "80 Build" / "scripts" / "publish.sh"
        self.spreadsheet_builder = (
            self.paths.root / "80 Build" / "scripts" / "build-all-spreadsheet-downloads.sh"
        )
        self.status_reporter = self.paths.root / "80 Build" / "scripts" / "git-status-report.sh"
        self._note_reviews = {}
        self._publish_reviews = {}

    def _run(self, command, *, timeout=15 * 60, cwd=None, env=None):
        try:
            return subprocess.run(
                command,
                cwd=cwd or self.paths.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise PublicationWorkflowError(f"{Path(command[0]).name} timed out.") from exc
        except OSError as exc:
            raise PublicationWorkflowError(f"Could not run {Path(command[0]).name}: {exc}") from exc

    def _git(self, *arguments):
        result = self._run(["git", *arguments], timeout=3 * 60)
        if result.returncode:
            raise PublicationWorkflowError(
                result.stdout.strip() or f"Git command failed: {' '.join(arguments)}"
            )
        return result.stdout.strip()

    @staticmethod
    def _pending_count(value):
        try:
            pending = int(value)
        except (TypeError, ValueError) as exc:
            raise PublicationWorkflowError("Pending browser draft count must be an integer.") from exc
        if pending < 0:
            raise PublicationWorkflowError("Pending browser draft count cannot be negative.")
        return pending

    def _metadata(self):
        try:
            payload = yaml.safe_load(self.metadata_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise PublicationWorkflowError(f"Publication metadata could not be read: {exc}") from exc
        version = (payload or {}).get("version") or {}
        major, minor = version.get("major"), version.get("minor")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (major, minor)):
            raise PublicationWorkflowError("Publication metadata has an invalid version.")
        return payload

    def _version_choice(self, major_version=None):
        current = self._metadata()["version"]
        current_label = f"{current['major']}.{current['minor']:02d}"
        if major_version in {None, ""}:
            major = None
            next_label = f"{current['major']}.{current['minor'] + 1:02d}"
            kind = "minor"
        else:
            try:
                major = int(major_version)
            except (TypeError, ValueError) as exc:
                raise PublicationWorkflowError("A major release number must be an integer.") from exc
            if isinstance(major_version, bool) or major <= current["major"]:
                raise PublicationWorkflowError(
                    f"A major release number must be greater than {current['major']}."
                )
            next_label = f"{major}.00"
            kind = "major"
        return {
            "currentVersion": current_label,
            "nextVersion": next_label,
            "releaseKind": kind,
            "majorVersion": major,
        }

    def _notes(self):
        try:
            return load_release_notes(self.notes_path)
        except Exception as exc:
            raise PublicationWorkflowError(str(exc)) from exc

    def _spreadsheet_state(self):
        script = self.paths.root / "80 Build" / "spreadsheet_downloads.py"
        if not script.is_file():
            return {"status": "unavailable", "output": "Spreadsheet readiness tool is missing."}
        result = self._run([sys.executable, str(script), "all", "diagnose"], timeout=5 * 60)
        output = result.stdout[-80_000:].strip()
        if result.returncode == 0:
            status = "current"
            refresh_targets = []
        elif result.returncode == 2:
            status = "refresh-needed"
            refresh_targets = []
            if "- Matrix/settings:" in output:
                refresh_targets.append("matrix")
            if "- Setup:" in output:
                refresh_targets.append("setup")
        else:
            status = "blocked"
            refresh_targets = []
        return {
            "status": status,
            "refreshTargets": refresh_targets,
            "buildIds": {
                target: spreadsheet_build_id(self.paths, target)
                for target in ("matrix", "setup")
            },
            "output": output,
        }

    def inspect(self, pending_changes=0, major_version=None, *, refresh=True):
        pending = self._pending_count(pending_changes)
        version = self._version_choice(major_version)
        branch = self._git("branch", "--show-current")
        blockers = []
        if pending:
            blockers.append(
                f"Resolve {pending} unsaved browser {'draft' if pending == 1 else 'drafts'} before publishing."
            )
        if branch != "main":
            return {
                **version,
                "phase": "main-handoff",
                "branch": branch or None,
                "upstream": None,
                "notesReady": False,
                "highlights": [],
                "spreadsheetState": {"status": "not-checked", "output": ""},
                "blockers": blockers + ["Live publication is available only from the Main project editor."],
                "output": f"Current branch: {branch or 'detached HEAD'}",
            }
        if refresh:
            fetched = self._run(["git", "fetch", "--prune", "origin"], timeout=5 * 60)
            if fetched.returncode:
                blockers.append(fetched.stdout.strip() or "Origin could not be refreshed.")
        try:
            upstream = self._git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        except PublicationWorkflowError as exc:
            upstream = None
            blockers.append(str(exc))
        if upstream and upstream != "origin/main":
            blockers.append(f"Main must track origin/main, not {upstream}.")
        status = self._git("status", "--porcelain=v1", "--untracked-files=all")
        if status:
            blockers.append("Finish Day must leave main clean before publication.")
        if upstream == "origin/main":
            head = self._git("rev-parse", "HEAD")
            remote = self._git("rev-parse", "origin/main")
            if head != remote:
                blockers.append("Main must be synchronized with origin/main before publication.")
        notes = self._notes()
        highlights = notes.get(version["nextVersion"], [])
        spreadsheet_state = self._spreadsheet_state()
        if spreadsheet_state["status"] == "blocked":
            blockers.append("Spreadsheet publication readiness could not be determined.")
        if blockers:
            phase = "blocked"
        elif not highlights:
            phase = "release-notes"
        else:
            phase = "ready"
        recovery_actions = []
        if pending:
            recovery_actions.append("open-review-build")
        if any("Finish Day" in blocker or "synchronized" in blocker for blocker in blockers):
            recovery_actions.append("open-finish-day")
        if spreadsheet_state["status"] == "blocked":
            recovery_actions.append("open-review-build")
        if blockers:
            recovery_actions.append("retry-publication-status")
        return {
            **version,
            "phase": phase,
            "branch": branch,
            "upstream": upstream,
            "notesReady": bool(highlights),
            "highlights": highlights,
            "spreadsheetState": spreadsheet_state,
            "recoveryActions": list(dict.fromkeys(recovery_actions)),
            "blockers": blockers,
            "output": "\n".join(part for part in (f"Branch: {branch}", f"Upstream: {upstream or 'unavailable'}", status) if part),
        }

    @staticmethod
    def _clean_highlights(highlights):
        if not isinstance(highlights, list):
            raise PublicationWorkflowError("Release highlights must be a list.")
        cleaned = [" ".join(str(item or "").split()) for item in highlights]
        cleaned = [item for item in cleaned if item]
        if not cleaned:
            raise PublicationWorkflowError("Add at least one reader-facing release highlight.")
        if len(cleaned) > 8:
            raise PublicationWorkflowError("Use no more than eight release highlights.")
        if len(set(cleaned)) != len(cleaned):
            raise PublicationWorkflowError("Release highlights must not be duplicated.")
        if any(len(item) > 500 for item in cleaned):
            raise PublicationWorkflowError("Each release highlight must be 500 characters or fewer.")
        return cleaned

    def _notes_candidate(self, version, highlights):
        source = self.notes_path.read_text(encoding="utf-8")
        notes = self._notes()
        if version in notes:
            raise PublicationWorkflowError(f"Release notes for Version {version} already exist.")
        lines = [source.rstrip(), f'  "{version}":', "    highlights:"]
        for highlight in highlights:
            scalar = json.dumps(highlight, ensure_ascii=False)
            lines.append(f"      - {scalar}")
        candidate = "\n".join(lines) + "\n"
        try:
            parsed = yaml.safe_load(candidate)
        except yaml.YAMLError as exc:
            raise PublicationWorkflowError(f"Release-note candidate is invalid: {exc}") from exc
        if not isinstance(parsed, dict):
            raise PublicationWorkflowError("Release-note candidate is invalid.")
        return source, candidate

    def review_release_notes(self, major_version, highlights):
        if self._git("branch", "--show-current") != "main":
            raise PublicationWorkflowError("Release notes for publication may be added only in the Main project editor.")
        if self._git("status", "--porcelain=v1", "--untracked-files=all"):
            raise PublicationWorkflowError("Finish Day must leave main clean before adding publication release notes.")
        version = self._version_choice(major_version)
        cleaned = self._clean_highlights(highlights)
        source, candidate = self._notes_candidate(version["nextVersion"], cleaned)
        token = secrets.token_urlsafe(24)
        self._note_reviews = {
            token: {
                "sourceHash": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "candidate": candidate,
                "version": version["nextVersion"],
                "highlights": cleaned,
            }
        }
        diff = "".join(
            difflib.unified_diff(
                source.splitlines(keepends=True),
                candidate.splitlines(keepends=True),
                fromfile="00 Master/release_notes.yaml",
                tofile="00 Master/release_notes.yaml (reviewed)",
            )
        )
        return {**version, "reviewToken": token, "highlights": cleaned, "diff": diff}

    def _backup_notes(self, review):
        timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
        backup = self.paths.backups_dir / f"{timestamp}-publication-release-notes"
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(self.notes_path, backup / self.notes_path.name)
        (backup / "transaction.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "created": datetime.now().astimezone().isoformat(),
                    "operation": "add-publication-release-notes",
                    "release": review["version"],
                    "source_sha256": review["sourceHash"],
                    "candidate_sha256": hashlib.sha256(review["candidate"].encode("utf-8")).hexdigest(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return backup

    def save_release_notes(self, review_token, confirmed):
        if confirmed is not True:
            raise PublicationWorkflowError("Release-note save confirmation is required.")
        review = self._note_reviews.pop(str(review_token or ""), None)
        if not review:
            raise PublicationWorkflowError("Release-note review expired. Review the highlights again.")
        current = self.notes_path.read_text(encoding="utf-8")
        if hashlib.sha256(current.encode("utf-8")).hexdigest() != review["sourceHash"]:
            raise PublicationWorkflowError("Release notes changed after review. Review them again.")
        backup = self._backup_notes(review)
        temporary = self.notes_path.with_name(f".{self.notes_path.name}.publication.tmp")
        temporary.write_text(review["candidate"], encoding="utf-8")
        temporary.replace(self.notes_path)
        validation = self._run([sys.executable, "80 Build/validator.py", "--source-only"], timeout=15 * 60)
        if validation.returncode:
            shutil.copy2(backup / self.notes_path.name, self.notes_path)
            raise PublicationWorkflowError(
                "Release-note validation failed; the original file was restored.\n"
                + validation.stdout[-80_000:].strip()
            )
        return {
            "version": review["version"],
            "highlights": review["highlights"],
            "backup": str(backup),
            "message": "Release notes saved and validated. Run Finish Day before publishing.",
        }

    def review_publication(self, pending_changes, major_version, spreadsheet_mode):
        if spreadsheet_mode not in self.SPREADSHEET_MODES:
            raise PublicationWorkflowError("Choose a valid spreadsheet publication option.")
        spreadsheet_mode = {
            "preserve": "automatic",
            "replace": "force",
        }.get(spreadsheet_mode, spreadsheet_mode)
        state = self.inspect(pending_changes, major_version)
        if state["phase"] != "ready":
            detail = " ".join(state["blockers"]) or f"Release notes for Version {state['nextVersion']} are required."
            raise PublicationWorkflowError("Publication review is blocked. " + detail)
        if spreadsheet_mode == "automatic":
            spreadsheet_targets = list(state["spreadsheetState"].get("refreshTargets") or [])
            if state["spreadsheetState"]["status"] == "refresh-needed" and not spreadsheet_targets:
                spreadsheet_targets = ["matrix", "setup"]
        elif spreadsheet_mode == "force":
            spreadsheet_targets = ["matrix", "setup"]
        else:
            spreadsheet_targets = []
        head = self._git("rev-parse", "HEAD")
        build_ids = state["spreadsheetState"].get("buildIds") or {
            target: spreadsheet_build_id(self.paths, target)
            for target in ("matrix", "setup")
        }
        token = secrets.token_urlsafe(24)
        review = {
            "token": token,
            "head": head,
            "version": state["nextVersion"],
            "majorVersion": state["majorVersion"],
            "spreadsheetMode": spreadsheet_mode,
            "spreadsheetTargets": spreadsheet_targets,
            "spreadsheetBuildIds": build_ids,
        }
        self._publish_reviews = {token: review}
        labels = {
            "automatic": (
                "Automatically rebuild stale workbook families"
                if spreadsheet_targets
                else "Preserve the current verified workbook downloads"
            ),
            "force": "Force-rebuild and replace both workbook download families",
            "remove": "Remove all published workbook downloads",
        }
        return {
            **state,
            "reviewToken": token,
            "spreadsheetMode": spreadsheet_mode,
            "spreadsheetTargets": spreadsheet_targets,
            "spreadsheetBuildIds": build_ids,
            "spreadsheetLabel": labels[spreadsheet_mode],
            "summary": (
                f"Publish Version {state['nextVersion']} to the live website. "
                f"{labels[spreadsheet_mode]}. "
                f"Spreadsheet builds: Matrix {build_ids['matrix']}; Setup {build_ids['setup']}."
                if spreadsheet_mode != "remove"
                else f"Publish Version {state['nextVersion']} to the live website. {labels[spreadsheet_mode]}."
            ),
        }

    @staticmethod
    def _notify(progress, stage, command="", output="", completed=False):
        if progress:
            progress(stage, command=command, output=output, completed=completed)

    def publish(self, review_token, confirmed, progress=None):
        if confirmed is not True:
            raise PublicationWorkflowError("Live website publication requires final confirmation.")
        review = self._publish_reviews.pop(str(review_token or ""), None)
        if not review:
            raise PublicationWorkflowError("Publication review expired. Review the release again.")
        state = self.inspect(0, review["majorVersion"])
        if state["phase"] != "ready" or self._git("rev-parse", "HEAD") != review["head"]:
            raise PublicationWorkflowError("Main changed after publication review. Review the release again.")
        steps = []
        spreadsheet_targets = tuple(review.get("spreadsheetTargets") or ())
        if spreadsheet_targets:
            command = [str(self.spreadsheet_builder)]
            display_builder = "$ build-all-spreadsheet-downloads"
            if review["spreadsheetMode"] == "force":
                command.append("--force-release-workbooks")
                display_builder += " --force-release-workbooks"
            self._notify(progress, "Preparing spreadsheet downloads", display_builder)
            built = self._run(command, timeout=45 * 60)
            output = built.stdout[-80_000:].strip()
            if built.returncode:
                recovery = numbers_resume_recovery(output, "resume-publication")
                if recovery:
                    self._publish_reviews[review["token"]] = review
                    recovery["reviewToken"] = review["token"]
                raise PublicationWorkflowError(
                    "Spreadsheet preparation failed.\n" + output,
                    recovery=recovery,
                )
            steps.append({"label": "Spreadsheet preparation", "status": "passed", "output": output})
            self._notify(progress, "Preparing spreadsheet downloads", output=output, completed=True)
        command = [str(self.publisher)]
        if review["majorVersion"] is not None:
            command.extend(["--major-version", str(review["majorVersion"])])
        if set(spreadsheet_targets) == {"matrix", "setup"}:
            command.append("--spreadsheet-downloads")
        elif spreadsheet_targets == ("matrix",):
            command.append("--matrix-downloads")
        elif spreadsheet_targets == ("setup",):
            command.append("--setup-downloads")
        elif review["spreadsheetMode"] == "remove":
            command.append("--remove-spreadsheet-downloads")
        display = "$ publish.sh"
        if review["majorVersion"] is not None:
            display += f" --major-version {review['majorVersion']}"
        if set(spreadsheet_targets) == {"matrix", "setup"}:
            display += " --spreadsheet-downloads"
        elif spreadsheet_targets == ("matrix",):
            display += " --matrix-downloads"
        elif spreadsheet_targets == ("setup",):
            display += " --setup-downloads"
        elif review["spreadsheetMode"] == "remove":
            display += " --remove-spreadsheet-downloads"
        self._notify(progress, "Publishing and verifying the live website", display)
        published = self._run(command, timeout=45 * 60)
        publish_output = published.stdout[-80_000:].strip()
        if published.returncode or "PUBLICATION COMPLETE AND VERIFIED." not in publish_output:
            raise PublicationWorkflowError("Publication did not complete.\n" + publish_output)
        steps.append({"label": "Website publication", "status": "passed", "output": publish_output})
        self._notify(progress, "Publishing and verifying the live website", output=publish_output, completed=True)
        self._notify(progress, "Confirming final synchronization", "$ git-status-report")
        status = self._run([str(self.status_reporter)], timeout=5 * 60)
        status_output = status.stdout[-80_000:].strip()
        if status.returncode or "STATUS: CLEAN AND SYNCHRONIZED" not in status_output:
            raise PublicationWorkflowError(
                "The website publisher completed, but final Git synchronization was not confirmed.\n"
                + status_output
            )
        steps.append({"label": "Final synchronization", "status": "passed", "output": status_output})
        self._notify(progress, "Confirming final synchronization", output=status_output, completed=True)
        build_ids = review.get("spreadsheetBuildIds", {}) if review["spreadsheetMode"] != "remove" else {}
        build_receipt = ""
        if build_ids:
            build_receipt = (
                f" Spreadsheet builds: Matrix {build_ids['matrix']}; Setup {build_ids['setup']}."
            )
        return {
            "phase": "complete",
            "version": review["version"],
            "spreadsheetMode": review["spreadsheetMode"],
            "spreadsheetTargets": list(spreadsheet_targets),
            "spreadsheetBuildIds": build_ids,
            "steps": steps,
            "message": f"Version {review['version']} is published and verified. Main is clean and synchronized.{build_receipt}",
            "output": "\n\n".join(step["output"] for step in steps if step["output"]),
        }


class MainEditorLauncher:
    """Open the main-worktree Profile Editor without exposing a terminal step."""

    def __init__(self, root):
        self.root = Path(root).resolve()

    def _main_worktree(self):
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise PublicationWorkflowError(result.stderr.strip() or "Git worktrees could not be inspected.")
        worktree = None
        for line in result.stdout.splitlines() + [""]:
            if line.startswith("worktree "):
                worktree = Path(line.removeprefix("worktree ")).resolve()
            elif line == "branch refs/heads/main" and worktree:
                return worktree
        raise PublicationWorkflowError("A checked-out Main project worktree was not found.")

    def launch(self):
        main_root = self._main_worktree()
        launcher = main_root / "80 Build" / "scripts" / "start-profile-editor.sh"
        if not launcher.is_file() or not os.access(launcher, os.X_OK):
            raise PublicationWorkflowError("The Main project Profile Editor launcher is unavailable.")
        local_workspace = Path(f"{main_root} Local").resolve()
        log_file = local_workspace / "Logs" / "R5 Profile Editor handoff.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("ab") as log_handle:
            environment = dict(os.environ)
            environment.pop("PRS_LOCAL_WORKSPACE", None)
            subprocess.Popen(
                [str(launcher)],
                cwd=main_root,
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=environment,
            )
        return {"started": True, "mainRoot": str(main_root), "url": "http://127.0.0.1:8765/"}
