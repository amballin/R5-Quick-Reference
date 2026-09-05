#!/usr/bin/env python3
"""Tests for the owner-controlled application profile catalog policy."""

from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

from validators.profile_catalog_policy_validator import validate


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProfileCatalogPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "00 Master").mkdir(parents=True)
        shutil.copytree(PROJECT_ROOT / "10 Profiles", self.root / "10 Profiles")
        for relative in (
            "00 Master/profile_catalog_policy.yaml",
            "00 Master/profile_lens_guidance.yaml",
        ):
            shutil.copy2(PROJECT_ROOT / relative, self.root / relative)

    def tearDown(self):
        self.temporary.cleanup()

    def test_current_catalog_policy_is_complete(self):
        self.assertEqual(validate(PROJECT_ROOT), [])

    def test_rejects_missing_extra_or_moved_profile_files(self):
        missing = self.root / "10 Profiles" / "Macro.yaml"
        missing.unlink()
        issues = validate(self.root)
        self.assertTrue(any("missing or moved: Macro.yaml" in issue.message for issue in issues))

        shutil.copy2(PROJECT_ROOT / "10 Profiles" / "Macro.yaml", missing)
        nested = self.root / "10 Profiles" / "Nested"
        nested.mkdir()
        missing.rename(nested / "Macro.yaml")
        issues = validate(self.root)
        self.assertTrue(any("missing or moved: Macro.yaml" in issue.message for issue in issues))
        self.assertTrue(any("Nested/Macro.yaml" in issue.message for issue in issues))

        shutil.copy2(PROJECT_ROOT / "10 Profiles" / "Macro.yaml", missing)
        shutil.copy2(PROJECT_ROOT / "10 Profiles" / "Macro.yaml", nested / "Extra.yaml")
        issues = validate(self.root)
        self.assertTrue(any("Unregistered catalog files" in issue.message for issue in issues))

    def test_rejects_filename_identity_and_policy_path_changes(self):
        macro = self.root / "10 Profiles" / "Macro.yaml"
        profile = yaml.safe_load(macro.read_text(encoding="utf-8"))
        profile["card_id"] = "00000000-0000-0000-0000-000000000001"
        macro.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("do not match" in issue.message for issue in validate(self.root)))

        policy_path = self.root / "00 Master" / "profile_catalog_policy.yaml"
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        policy["protected_sources"]["profile_directory"] = "Catalog"
        policy_path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("source paths changed" in issue.message for issue in validate(self.root)))

    def test_rejects_duplicate_filename_and_identity(self):
        policy_path = self.root / "00 Master" / "profile_catalog_policy.yaml"
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        policy["profiles"][1]["card_id"] = policy["profiles"][0]["card_id"]
        policy_path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("Duplicate catalog card_id" in issue.message for issue in validate(self.root)))

        policy = yaml.safe_load((PROJECT_ROOT / "00 Master/profile_catalog_policy.yaml").read_text(encoding="utf-8"))
        policy["profiles"][1]["filename"] = policy["profiles"][0]["filename"]
        policy_path.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("Duplicate catalog filename" in issue.message for issue in validate(self.root)))

    def test_rejects_unknown_lens_guidance_identity(self):
        policy_path = self.root / "00 Master" / "profile_catalog_policy.yaml"
        shutil.copy2(PROJECT_ROOT / "00 Master/profile_catalog_policy.yaml", policy_path)
        guidance_path = self.root / "00 Master" / "profile_lens_guidance.yaml"
        guidance = yaml.safe_load(guidance_path.read_text(encoding="utf-8"))
        guidance["profiles"].append({"card_id": "00000000-0000-0000-0000-000000000001", "choices": []})
        guidance_path.write_text(yaml.safe_dump(guidance, sort_keys=False), encoding="utf-8")
        self.assertTrue(any("outside the protected catalog" in issue.message for issue in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
