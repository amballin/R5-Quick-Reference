import subprocess
import tempfile
import unittest
from pathlib import Path

from profile_pack_git import ProfilePackGitError, ProfilePackGitWorkflow


class ProfilePackGitWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.application = base / "application"
        self.pack = base / "pack"
        self.application.mkdir()
        self.pack.mkdir()
        self._init(self.application)
        self._init(self.pack)
        (self.application / "app.txt").write_text("application\n", encoding="utf-8")
        self._commit_all(self.application, "Initialize application")
        self.application_remote = base / "application.git"
        self._bare_remote(self.application_remote)
        self._git(self.application, "remote", "add", "origin", str(self.application_remote))
        self._git(self.application, "push", "-u", "origin", "main")
        (self.pack / "profile-pack.yaml").write_text("pack_id: test-pack\n", encoding="utf-8")
        (self.pack / "AGENTS.md").write_text("# Private pack rules\n", encoding="utf-8")
        (self.pack / "profile.yaml").write_text("title: Birds\n", encoding="utf-8")
        self.workflow = ProfilePackGitWorkflow(
            self.application, self.pack, "test-pack", allow_local_remotes=True
        )

    def tearDown(self):
        self.temporary.cleanup()

    def _run(self, command, *, cwd=None):
        return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)

    def _git(self, root, *args):
        return self._run(["git", *args], cwd=root)

    def _init(self, root):
        self._run(["git", "init", "-b", "main", str(root)])
        self._git(root, "config", "user.name", "Profile Pack Test")
        self._git(root, "config", "user.email", "profile-pack@example.invalid")

    def _commit_all(self, root, message):
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", message)

    def _bare_remote(self, path):
        self._run(["git", "init", "--bare", "-b", "main", str(path)])

    def test_initial_review_requires_and_commits_agents(self):
        application_head = self._git(self.application, "rev-parse", "HEAD").stdout.strip()
        application_status = self._git(self.application, "status", "--porcelain=v1").stdout
        status = self.workflow.inspect(0)
        self.assertEqual(status["phase"], "initial-commit")
        review = self.workflow.review_commit(0)
        self.assertTrue(review["includesAgents"])
        result = self.workflow.commit(
            review["reviewToken"], "Initialize private profile pack", True
        )
        self.assertIn("AGENTS.md", result["committedFiles"])
        self.assertEqual(result["phase"], "remote")
        self.assertFalse(result["pack"]["originConfigured"])
        self.assertEqual(self._git(self.application, "rev-parse", "HEAD").stdout.strip(), application_head)
        self.assertEqual(self._git(self.application, "status", "--porcelain=v1").stdout, application_status)
        self.assertEqual(self._git(self.pack, "branch", "--show-current").stdout.strip(), "main")

    def test_initial_review_rejects_missing_agents(self):
        (self.pack / "AGENTS.md").unlink()
        with self.assertRaisesRegex(ProfilePackGitError, "must include AGENTS.md"):
            self.workflow.review_commit(0)

    def test_commit_review_is_one_use_and_source_bound(self):
        review = self.workflow.review_commit(0)
        (self.pack / "profile.yaml").write_text("title: Wildlife\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackGitError, "changed after review"):
            self.workflow.commit(review["reviewToken"], "Changed", True)

    def test_remote_review_rejects_embedded_credentials(self):
        review = self.workflow.review_commit(0)
        self.workflow.commit(review["reviewToken"], "Initialize pack", True)
        with self.assertRaisesRegex(ProfilePackGitError, "embedded credentials"):
            self.workflow.review_remote("https://secret@example.com/private.git", 0)
        with self.assertRaisesRegex(ProfilePackGitError, "query values"):
            self.workflow.review_remote("https://example.com/private.git?token=secret", 0)

    def test_remote_review_is_source_bound(self):
        review = self.workflow.review_commit(0)
        self.workflow.commit(review["reviewToken"], "Initialize pack", True)
        remote = Path(self.temporary.name) / "pack.git"
        self._bare_remote(remote)
        remote_review = self.workflow.review_remote(str(remote), 0)
        (self.pack / "profile.yaml").write_text("title: Changed after remote review\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfilePackGitError, "changed after remote review"):
            self.workflow.configure_remote(remote_review["reviewToken"], True)

    def test_remote_and_push_are_separate_and_handoff_requires_both_repositories(self):
        commit_review = self.workflow.review_commit(0)
        self.workflow.commit(commit_review["reviewToken"], "Initialize pack", True)
        remote = Path(self.temporary.name) / "pack.git"
        self._bare_remote(remote)
        remote_review = self.workflow.review_remote(str(remote), 0)
        configured = self.workflow.configure_remote(remote_review["reviewToken"], True)
        self.assertEqual(configured["phase"], "push")
        self.assertFalse(configured["pack"]["synchronized"])
        pushed = self.workflow.push(True)
        self.assertTrue(pushed["pack"]["synchronized"])
        self.assertTrue(pushed["application"]["synchronized"])
        self.assertTrue(pushed["handoff"]["ready"])

    def test_pending_browser_drafts_block_pack_git_review(self):
        status = self.workflow.inspect(2)
        self.assertEqual(status["phase"], "blocked")
        with self.assertRaisesRegex(ProfilePackGitError, "blocked"):
            self.workflow.review_commit(2)

    def test_push_rejects_remote_only_work(self):
        commit_review = self.workflow.review_commit(0)
        self.workflow.commit(commit_review["reviewToken"], "Initialize pack", True)
        remote = Path(self.temporary.name) / "pack.git"
        self._bare_remote(remote)
        remote_review = self.workflow.review_remote(str(remote), 0)
        self.workflow.configure_remote(remote_review["reviewToken"], True)
        self.workflow.push(True)
        other = Path(self.temporary.name) / "other"
        self._git(Path(self.temporary.name), "clone", str(remote), str(other))
        self._git(other, "config", "user.name", "Profile Pack Test")
        self._git(other, "config", "user.email", "profile-pack@example.invalid")
        (other / "remote.txt").write_text("remote-only\n", encoding="utf-8")
        self._commit_all(other, "Remote-only work")
        self._git(other, "push", "origin", "main")
        with self.assertRaisesRegex(ProfilePackGitError, "contains work not present locally"):
            self.workflow.push(True)


if __name__ == "__main__":
    unittest.main()
