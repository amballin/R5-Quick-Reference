#!/usr/bin/env python3
"""Guarded Git workflow for one independently owned private profile pack."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import secrets
import subprocess
from urllib.parse import urlsplit, urlunsplit


class ProfilePackGitError(RuntimeError):
    pass


class ProfilePackGitWorkflow:
    REVIEW_TTL_SECONDS = 30 * 60
    SCP_REMOTE = re.compile(r"^[A-Za-z0-9._-]+@[A-Za-z0-9.-]+:[^\s]+$")
    IGNORED_METADATA_NAMES = {".DS_Store"}

    def __init__(self, application_root, pack_root, pack_id, *, allow_local_remotes=False):
        self.application_root = Path(application_root).resolve()
        self.pack_root = Path(pack_root).resolve()
        self.pack_id = str(pack_id)
        self.allow_local_remotes = allow_local_remotes
        self._commit_review = None
        self._remote_review = None
        self._assert_repository()

    def _run(self, root, command, *, timeout=3 * 60, env=None):
        try:
            return subprocess.run(
                command,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProfilePackGitError(
                f"The Git service did not respond within {timeout} seconds. The action stopped; refresh status before trying again."
            ) from exc
        except OSError as exc:
            raise ProfilePackGitError(f"Could not run {Path(command[0]).name}: {exc}") from exc

    def _git(self, root, *args, check=True, env=None, timeout=3 * 60):
        completed = self._run(root, ["git", *args], env=env, timeout=timeout)
        output = completed.stdout.strip()
        if check and completed.returncode:
            raise ProfilePackGitError(output or f"Git command failed: {' '.join(args)}")
        return completed

    def _assert_repository(self):
        if self.pack_root == self.application_root:
            raise ProfilePackGitError("The private profile pack must be a repository separate from the application.")
        top = self._git(self.pack_root, "rev-parse", "--show-toplevel").stdout.strip()
        if Path(top).resolve() != self.pack_root:
            raise ProfilePackGitError("The selected profile pack is not the root of its own Git repository.")
        if not (self.pack_root / "profile-pack.yaml").is_file():
            raise ProfilePackGitError("The selected Git repository does not contain profile-pack.yaml.")

    @staticmethod
    def _pending_count(value):
        try:
            count = int(value)
        except (TypeError, ValueError) as exc:
            raise ProfilePackGitError("Pending browser draft count must be an integer.") from exc
        if count < 0:
            raise ProfilePackGitError("Pending browser draft count cannot be negative.")
        return count

    def _head_exists(self, root):
        return self._git(root, "rev-parse", "--verify", "HEAD", check=False).returncode == 0

    def _branch(self, root):
        branch = self._git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        value = branch.stdout.strip()
        if branch.returncode or not value:
            raise ProfilePackGitError("Git work is unavailable on a detached checkout.")
        return value

    def _status_lines(self, root):
        output = self._git(root, "status", "--porcelain=v1", "--untracked-files=all").stdout
        return [
            line for line in output.splitlines()
            if line.strip() and Path(line[3:].strip('"')).name not in self.IGNORED_METADATA_NAMES
        ]

    def _snapshot(self):
        digest = hashlib.sha256()
        for relative in sorted(
            path.relative_to(self.pack_root).as_posix()
            for path in self.pack_root.rglob("*")
            if path.is_file()
            and ".git" not in path.relative_to(self.pack_root).parts
            and path.name not in self.IGNORED_METADATA_NAMES
        ):
            path = self.pack_root / relative
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        digest.update("\n".join(self._status_lines(self.pack_root)).encode("utf-8"))
        return digest.hexdigest()

    def _origin(self, root):
        result = self._git(root, "remote", "get-url", "origin", check=False)
        return result.stdout.strip() if result.returncode == 0 else ""

    @classmethod
    def _display_remote(cls, value):
        if not value:
            return ""
        parts = urlsplit(value)
        if parts.scheme in {"http", "https", "ssh"} and parts.hostname:
            host = parts.hostname
            if parts.port:
                host += f":{parts.port}"
            if parts.scheme == "ssh" and parts.username:
                host = f"{parts.username}@{host}"
            return urlunsplit((parts.scheme, host, parts.path, parts.query, ""))
        return value

    def _validate_remote(self, value):
        remote = str(value or "").strip()
        if not remote or any(char.isspace() for char in remote):
            raise ProfilePackGitError("Enter one exact remote URL without spaces.")
        parts = urlsplit(remote)
        if parts.scheme in {"https", "http", "ssh"} and parts.hostname:
            if parts.password:
                raise ProfilePackGitError("Remote URLs containing embedded credentials are not allowed.")
            if parts.scheme in {"https", "http"} and parts.username:
                raise ProfilePackGitError("Remote URLs containing embedded credentials are not allowed.")
            if parts.query or parts.fragment:
                raise ProfilePackGitError("Remote URLs containing query values or fragments are not allowed.")
            return remote
        if self.SCP_REMOTE.fullmatch(remote):
            return remote
        if self.allow_local_remotes and Path(remote).is_absolute():
            return str(Path(remote).resolve())
        raise ProfilePackGitError("Use an HTTPS or SSH Git remote URL. Credentials must remain in the system credential manager.")

    def _repository_status(self, root, *, label):
        branch = self._branch(root)
        status_lines = self._status_lines(root)
        head_exists = self._head_exists(root)
        local_head = self._git(root, "rev-parse", "HEAD").stdout.strip() if head_exists else ""
        origin = self._origin(root)
        upstream_result = self._git(
            root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", check=False
        )
        upstream = upstream_result.stdout.strip() if upstream_result.returncode == 0 else ""
        ahead = behind = None
        blocker = ""
        synchronized = False
        remote_head = ""
        remote_check = "not-configured"
        if head_exists and origin:
            try:
                remote = self._git(
                    root,
                    "ls-remote",
                    "--exit-code",
                    "origin",
                    f"refs/heads/{branch}",
                    check=False,
                    env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
                    timeout=20,
                )
            except ProfilePackGitError as exc:
                remote_check = "unavailable"
                blocker = str(exc)
            else:
                if remote.returncode == 0 and remote.stdout.split():
                    remote_head = remote.stdout.split()[0]
                    remote_check = "found"
                elif remote.returncode == 2:
                    remote_check = "missing"
                else:
                    remote_check = "unavailable"
                    blocker = "The exact origin branch could not be checked without prompting for credentials."
        if head_exists and origin and upstream:
            expected = f"origin/{branch}"
            if upstream != expected:
                blocker = f"Branch '{branch}' tracks '{upstream}', not '{expected}'."
            else:
                counts = self._git(root, "rev-list", "--left-right", "--count", f"HEAD...{upstream}", check=False)
                try:
                    ahead, behind = (int(part) for part in counts.stdout.split())
                except (TypeError, ValueError):
                    blocker = "The local and remote branch comparison could not be determined."
                else:
                    synchronized = (
                        not status_lines
                        and ahead == 0
                        and behind == 0
                        and remote_check == "found"
                        and local_head == remote_head
                    )
                    if not blocker and ahead == 0 and behind == 0 and remote_check == "found" and local_head != remote_head:
                        blocker = "The exact origin branch changed after the last local fetch. Refresh it outside this workflow before handoff."
                    if behind and ahead:
                        blocker = "Local and remote histories have diverged. Resolve them outside this workflow."
                    elif behind:
                        blocker = "The local branch is behind its matching origin branch. Update it outside this workflow."
        return {
            "label": label,
            "branch": branch,
            "headExists": head_exists,
            "headShort": local_head[:7],
            "clean": not status_lines,
            "changes": status_lines,
            "originConfigured": bool(origin),
            "origin": self._display_remote(origin),
            "upstream": upstream,
            "ahead": ahead,
            "behind": behind,
            "synchronized": synchronized,
            "remoteCheck": remote_check,
            "blocker": blocker,
        }

    def inspect(self, pending_changes=0):
        pending = self._pending_count(pending_changes)
        self._assert_repository()
        pack = self._repository_status(self.pack_root, label="Private profile pack")
        application = self._repository_status(self.application_root, label="Application")
        blockers = []
        if pending:
            blockers.append(f"Resolve {pending} unsaved browser draft{'s' if pending != 1 else ''} first.")
        if pack["blocker"]:
            blockers.append(pack["blocker"])
        if not pack["headExists"]:
            phase = "initial-commit"
        elif not pack["clean"]:
            phase = "commit"
        elif not pack["originConfigured"]:
            phase = "remote"
        elif pack["blocker"]:
            phase = "blocked"
        elif not pack["upstream"] or (pack["ahead"] or 0) > 0:
            phase = "push"
        elif pack["synchronized"]:
            phase = "complete"
        else:
            phase = "blocked"
        if pending:
            phase = "blocked"
        handoff_blockers = []
        if not application["synchronized"]:
            handoff_blockers.append("The application repository is not clean and synchronized with its matching origin branch.")
        if not pack["synchronized"]:
            handoff_blockers.append("The private profile pack is not clean and synchronized with its matching origin branch.")
        return {
            "phase": phase,
            "packId": self.pack_id,
            "pendingChanges": pending,
            "blockers": blockers,
            "application": application,
            "pack": pack,
            "handoff": {"ready": not handoff_blockers, "blockers": handoff_blockers},
        }

    def review_commit(self, pending_changes=0):
        status = self.inspect(pending_changes)
        if status["phase"] == "blocked":
            raise ProfilePackGitError("Pack commit review is blocked. " + " ".join(status["blockers"]))
        if status["phase"] not in {"initial-commit", "commit"}:
            raise ProfilePackGitError("The private profile pack has no changes requiring a commit.")
        files = status["pack"]["changes"]
        if not files:
            raise ProfilePackGitError("The private profile pack has no files to commit.")
        if status["phase"] == "initial-commit" and not any(line[3:] == "AGENTS.md" for line in files):
            raise ProfilePackGitError("The initial private-pack commit must include AGENTS.md.")
        token = secrets.token_urlsafe(24)
        self._commit_review = {
            "token": token,
            "created": datetime.now(timezone.utc),
            "snapshot": self._snapshot(),
            "phase": status["phase"],
            "files": files,
            "branch": status["pack"]["branch"],
            "head": self._git(self.pack_root, "rev-parse", "HEAD", check=False).stdout.strip(),
        }
        return {
            "reviewToken": token,
            "phase": status["phase"],
            "branch": status["pack"]["branch"],
            "files": files,
            "includesAgents": any(line[3:] == "AGENTS.md" for line in files),
        }

    def commit(self, review_token, message, confirmed):
        if confirmed is not True:
            raise ProfilePackGitError("Pack commit confirmation is required.")
        review = self._commit_review
        if not review or not secrets.compare_digest(str(review_token or ""), review["token"]):
            raise ProfilePackGitError("Pack commit review expired. Review the exact files again.")
        if (datetime.now(timezone.utc) - review["created"]).total_seconds() > self.REVIEW_TTL_SECONDS:
            self._commit_review = None
            raise ProfilePackGitError("Pack commit review expired. Review the exact files again.")
        commit_message = " ".join(str(message or "").split())
        if not commit_message or len(commit_message) > 200:
            raise ProfilePackGitError("Enter a commit message between 1 and 200 characters.")
        if self._snapshot() != review["snapshot"]:
            self._commit_review = None
            raise ProfilePackGitError("The profile pack changed after review. Review the exact files again.")
        current_head = self._git(self.pack_root, "rev-parse", "HEAD", check=False).stdout.strip()
        if self._branch(self.pack_root) != review["branch"] or current_head != review["head"]:
            self._commit_review = None
            raise ProfilePackGitError("The private-pack branch or commit changed after review. Review the exact files again.")
        if review["phase"] == "initial-commit" and not (self.pack_root / "AGENTS.md").is_file():
            self._commit_review = None
            raise ProfilePackGitError("The initial private-pack commit must include AGENTS.md.")
        self._git(
            self.pack_root,
            "add",
            "-A",
            "--",
            ".",
            ":(exclude).DS_Store",
            ":(glob,exclude)**/.DS_Store",
        )
        staged = self._git(self.pack_root, "diff", "--cached", "--name-only").stdout.splitlines()
        if review["phase"] == "initial-commit" and "AGENTS.md" not in staged:
            raise ProfilePackGitError("AGENTS.md did not enter the reviewed initial commit. Nothing was committed.")
        self._git(self.pack_root, "commit", "-m", commit_message)
        self._commit_review = None
        result = self.inspect(0)
        result["committedFiles"] = staged
        result["commitMessage"] = commit_message
        result["receipt"] = {
            "action": "Private-pack commit",
            "packId": self.pack_id,
            "branch": self._branch(self.pack_root),
            "commit": self._git(self.pack_root, "rev-parse", "--short", "HEAD").stdout.strip(),
            "remote": self._display_remote(self._origin(self.pack_root)) or "Not configured",
            "completedAt": datetime.now(timezone.utc).isoformat(),
            "verified": "Committed locally; nothing was pushed.",
            "nextStep": "Create an empty private GitHub repository and connect it in Step 3.",
        }
        return result

    def review_remote(self, remote_url, pending_changes=0):
        pending = self._pending_count(pending_changes)
        if pending:
            raise ProfilePackGitError("Resolve every unsaved browser draft before configuring a remote.")
        self._assert_repository()
        if not self._head_exists(self.pack_root):
            raise ProfilePackGitError("Create the reviewed initial pack commit before configuring a remote.")
        remote = self._validate_remote(remote_url)
        branch = self._branch(self.pack_root)
        previous = self._origin(self.pack_root)
        token = secrets.token_urlsafe(24)
        self._remote_review = {
            "token": token,
            "created": datetime.now(timezone.utc),
            "snapshot": self._snapshot(),
            "remote": remote,
            "replacing": bool(previous),
            "branch": branch,
            "head": self._git(self.pack_root, "rev-parse", "HEAD").stdout.strip(),
            "previous": previous,
        }
        return {
            "reviewToken": token,
            "remote": self._display_remote(remote),
            "replacing": bool(previous),
            "previousRemote": self._display_remote(previous),
        }

    @staticmethod
    def _notify(progress, stage, command="", output="", completed=False):
        if progress:
            progress(stage, command=command, output=output, completed=completed)

    def configure_remote(self, review_token, confirmed, progress=None):
        if confirmed is not True:
            raise ProfilePackGitError("Remote configuration confirmation is required.")
        review = self._remote_review
        if not review or not secrets.compare_digest(str(review_token or ""), review["token"]):
            raise ProfilePackGitError("Remote review expired. Review the exact URL again.")
        if (datetime.now(timezone.utc) - review["created"]).total_seconds() > self.REVIEW_TTL_SECONDS:
            self._remote_review = None
            raise ProfilePackGitError("Remote review expired. Review the exact URL again.")
        if self._snapshot() != review["snapshot"]:
            self._remote_review = None
            raise ProfilePackGitError("The profile pack changed after remote review. Review the exact URL again.")
        if (
            self._branch(self.pack_root) != review["branch"]
            or self._git(self.pack_root, "rev-parse", "HEAD").stdout.strip() != review["head"]
            or self._origin(self.pack_root) != review["previous"]
        ):
            self._remote_review = None
            raise ProfilePackGitError("The private-pack branch, commit, or origin changed after review. Review the exact URL again.")
        command = ("set-url", "origin", review["remote"]) if review["replacing"] else ("add", "origin", review["remote"])
        self._notify(progress, "Saving the reviewed private origin", "Update only the selected profile pack's Git configuration")
        self._git(self.pack_root, "remote", *command)
        self._notify(progress, "Saving the reviewed private origin", output="Private origin saved. Nothing was pushed.", completed=True)
        self._remote_review = None
        self._notify(progress, "Checking private GitHub access", "Read the exact remote branch without changing either repository")
        result = self.inspect(0)
        self._notify(progress, "Checking private GitHub access", output="Remote access check completed.", completed=True)
        remote_verified = result["pack"]["remoteCheck"] != "unavailable"
        result["receipt"] = {
            "action": "Private origin configured",
            "packId": self.pack_id,
            "branch": result["pack"]["branch"],
            "commit": self._git(self.pack_root, "rev-parse", "--short", "HEAD").stdout.strip(),
            "remote": result["pack"]["origin"],
            "completedAt": datetime.now(timezone.utc).isoformat(),
            "verified": "Origin saved and GitHub access checked; nothing was pushed." if remote_verified else "Origin saved locally, but GitHub access could not be verified; nothing was pushed.",
            "nextStep": "Review, push, and verify this pack in Step 4." if remote_verified else "Check the URL and Mac credentials, then refresh status or review a replacement connection.",
        }
        return result

    def push(self, confirmed, progress=None):
        if confirmed is not True:
            raise ProfilePackGitError("Pack push confirmation is required.")
        status = self.inspect(0)
        pack = status["pack"]
        if not pack["headExists"] or not pack["clean"]:
            raise ProfilePackGitError("Commit every reviewed pack change before pushing.")
        if not pack["originConfigured"]:
            raise ProfilePackGitError("Configure and review the private pack's origin before pushing.")
        branch = pack["branch"]
        self._notify(progress, "Checking the exact private origin branch", f"Read origin/{branch} without prompting for credentials")
        remote = self._git(
            self.pack_root,
            "ls-remote",
            "--exit-code",
            "origin",
            f"refs/heads/{branch}",
            check=False,
            env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
            timeout=20,
        )
        if remote.returncode not in {0, 2}:
            raise ProfilePackGitError("The exact private origin branch could not be checked without prompting for credentials.")
        self._notify(progress, "Checking the exact private origin branch", output="Remote branch state checked.", completed=True)
        if remote.returncode == 0:
            self._notify(progress, "Refreshing the matching pack branch", f"Fetch only origin/{branch} into the private pack")
            self._git(
                self.pack_root,
                "fetch",
                "origin",
                f"refs/heads/{branch}:refs/remotes/origin/{branch}",
                env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
                timeout=60,
            )
            self._notify(progress, "Refreshing the matching pack branch", output="Matching remote branch refreshed.", completed=True)
            counts = self._git(
                self.pack_root,
                "rev-list",
                "--left-right",
                "--count",
                f"HEAD...origin/{branch}",
            ).stdout.split()
            ahead, behind = (int(part) for part in counts)
            if behind:
                raise ProfilePackGitError("The private origin branch contains work not present locally. Update it outside this workflow before pushing.")
        status = self.inspect(0)
        pack = status["pack"]
        if pack["blocker"]:
            raise ProfilePackGitError(pack["blocker"])
        if pack["upstream"] and pack["upstream"] != f"origin/{branch}":
            raise ProfilePackGitError("The current branch does not track its exact matching origin branch.")
        args = ("push", "--set-upstream", "origin", branch) if not pack["upstream"] else ("push", "origin", branch)
        self._notify(progress, "Pushing the private profile pack", f"Push only {branch} to origin/{branch}")
        self._git(self.pack_root, *args, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"), timeout=3 * 60)
        self._notify(progress, "Pushing the private profile pack", output="Push command completed.", completed=True)
        self._notify(progress, "Verifying the live GitHub commit", f"Compare the local commit with origin/{branch}")
        final = self.inspect(0)
        if not final["pack"]["synchronized"]:
            raise ProfilePackGitError("The push finished, but the private pack did not verify as synchronized.")
        commit = self._git(self.pack_root, "rev-parse", "--short", "HEAD").stdout.strip()
        self._notify(progress, "Verifying the live GitHub commit", output=f"Verified {commit} on origin/{branch}.", completed=True)
        final["receipt"] = {
            "action": "Private pack pushed",
            "packId": self.pack_id,
            "branch": branch,
            "commit": commit,
            "remote": final["pack"]["origin"],
            "completedAt": datetime.now(timezone.utc).isoformat(),
            "verified": f"Verified synchronized with origin/{branch}.",
            "nextStep": "Setup is complete. Refresh status at any time to verify both repositories again.",
        }
        return final
