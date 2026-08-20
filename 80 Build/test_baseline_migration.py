#!/usr/bin/env python3
"""Unit tests for deterministic baseline migration candidates."""

from copy import deepcopy
from datetime import date
from pathlib import Path
import sys
import unittest

import yaml


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from baseline_migration import BaselineMigrationError, build_migration_candidates


class BaselineMigrationCandidateTests(unittest.TestCase):
    def setUp(self):
        self.current = {"metadata": {"last_updated": date(2026, 1, 1)}, "defaults": {"mode": "old"}}
        self.proposed = {"metadata": {"last_updated": date(2026, 1, 1)}, "defaults": {"mode": "new"}}
        self.profiles = {
            "Alpha": {
                "metadata": {"last_updated": date(2026, 1, 1)},
                "title": "Alpha",
                "inherits": "baseline",
                "card": {"field_setup": {"my_menus": [{"name": "FAST", "settings": ["mode"]}]}},
                "overrides": {"mode": "new", "nested": {"keep": 1}},
            },
            "Beta": {
                "metadata": {"last_updated": date(2026, 1, 1)},
                "title": "Beta",
                "inherits": "baseline",
                "overrides": {},
            },
        }
        self.plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [{"profile": "Beta", "path": "mode", "override_value": "old"}],
            "overrides_to_remove": [{"profile": "Alpha", "path": "mode"}],
            "overrides_to_keep": [],
            "profile_card_cues_to_remove": [],
            "profile_card_cues_to_add": [{"profile": "Beta", "tab": "FAST", "path": "mode"}],
        }

    def test_builds_baseline_override_cleanup_and_card_cue_candidates(self):
        candidates = build_migration_candidates(
            self.current, self.proposed, self.profiles, self.plan, today=date(2026, 8, 19)
        )
        baseline = yaml.safe_load(candidates["00 Master/baseline.yaml"])
        alpha = yaml.safe_load(candidates["10 Profiles/Alpha.yaml"])
        beta = yaml.safe_load(candidates["10 Profiles/Beta.yaml"])
        self.assertEqual(baseline["defaults"]["mode"], "new")
        self.assertNotIn("mode", alpha["overrides"])
        self.assertEqual(alpha["overrides"]["nested"], {"keep": 1})
        self.assertEqual(beta["overrides"]["mode"], "old")
        self.assertEqual(beta["card"]["field_setup"]["my_menus"][0]["settings"], ["mode"])
        self.assertEqual(beta["metadata"]["last_updated"], date(2026, 8, 19))

    def test_does_not_mutate_inputs(self):
        snapshots = deepcopy((self.current, self.proposed, self.profiles, self.plan))
        build_migration_candidates(self.current, self.proposed, self.profiles, self.plan)
        self.assertEqual((self.current, self.proposed, self.profiles, self.plan), snapshots)

    def test_rejects_incomplete_plan(self):
        self.plan["complete"] = False
        with self.assertRaisesRegex(BaselineMigrationError, "complete"):
            build_migration_candidates(self.current, self.proposed, self.profiles, self.plan)

    def test_builds_profile_only_my_menu_cue_without_baseline_candidate(self):
        proposed = deepcopy(self.current)
        plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [],
            "overrides_to_remove": [],
            "overrides_to_keep": [],
            "profile_card_cues_to_add": [{"profile": "Beta", "tab": "FAST", "path": "mode"}],
        }
        candidates = build_migration_candidates(
            self.current, proposed, self.profiles, plan, today=date(2026, 8, 20)
        )
        self.assertNotIn("00 Master/baseline.yaml", candidates)
        beta = yaml.safe_load(candidates["10 Profiles/Beta.yaml"])
        self.assertEqual(beta["card"]["field_setup"]["my_menus"], [{"name": "FAST", "settings": ["mode"]}])
        self.assertNotIn("access_only", beta["card"]["field_setup"])

    def test_new_reference_category_route_is_access_only(self):
        profiles = {
            "Setup": {
                "metadata": {"last_updated": date(2026, 1, 1)},
                "title": "Setup",
                "display_category": "reference",
                "inherits": "baseline",
                "overrides": {},
            }
        }
        plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [],
            "overrides_to_remove": [],
            "overrides_to_keep": [],
            "profile_card_cues_to_add": [{"profile": "Setup", "tab": "FAST", "path": "mode"}],
        }
        candidates = build_migration_candidates(
            self.current, self.current, profiles, plan, today=date(2026, 8, 20)
        )
        setup = yaml.safe_load(candidates["10 Profiles/Setup.yaml"])["card"]["field_setup"]
        self.assertTrue(setup["access_only"])
        self.assertEqual(setup["my_menus"], [{"name": "FAST", "settings": ["mode"]}])

    def test_removes_only_planned_cue_and_empty_tab(self):
        profiles = deepcopy(self.profiles)
        profiles["Alpha"]["card"]["field_setup"]["my_menus"] = [
            {"name": "OLD", "settings": ["mode"]},
            {"name": "KEEP", "settings": ["nested.keep"]},
        ]
        plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [],
            "overrides_to_remove": [],
            "overrides_to_keep": [],
            "profile_card_cues_to_remove": [
                {"profile": "Alpha", "tab": "OLD", "path": "mode"}
            ],
            "profile_card_cues_to_add": [],
        }
        candidates = build_migration_candidates(
            self.current, self.current, profiles, plan, today=date(2026, 8, 20)
        )
        alpha = yaml.safe_load(candidates["10 Profiles/Alpha.yaml"])
        self.assertEqual(
            alpha["card"]["field_setup"]["my_menus"],
            [{"name": "KEEP", "settings": ["nested.keep"]}],
        )

    def test_moves_cue_between_tabs_in_one_candidate(self):
        profiles = deepcopy(self.profiles)
        plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [],
            "overrides_to_remove": [],
            "overrides_to_keep": [],
            "profile_card_cues_to_remove": [
                {"profile": "Alpha", "tab": "FAST", "path": "mode"}
            ],
            "profile_card_cues_to_add": [
                {"profile": "Alpha", "tab": "NEW", "path": "mode"}
            ],
        }
        candidates = build_migration_candidates(
            self.current, self.current, profiles, plan, today=date(2026, 8, 20)
        )
        alpha = yaml.safe_load(candidates["10 Profiles/Alpha.yaml"])
        self.assertEqual(
            alpha["card"]["field_setup"]["my_menus"],
            [{"name": "NEW", "settings": ["mode"]}],
        )

    def test_last_access_only_cue_removal_cleans_empty_route_scaffolding(self):
        profiles = {
            "Setup": {
                "metadata": {"last_updated": date(2026, 1, 1)},
                "title": "Setup",
                "display_category": "reference",
                "inherits": "baseline",
                "card": {
                    "field_setup": {
                        "access_only": True,
                        "my_menus": [{"name": "FAST", "settings": ["mode"]}],
                    }
                },
                "overrides": {},
            }
        }
        plan = {
            "complete": True,
            "unresolved_decisions": [],
            "profiles_following_baseline": [],
            "overrides_to_add": [],
            "overrides_to_remove": [],
            "overrides_to_keep": [],
            "profile_card_cues_to_remove": [
                {"profile": "Setup", "tab": "FAST", "path": "mode"}
            ],
            "profile_card_cues_to_add": [],
        }
        candidates = build_migration_candidates(
            self.current, self.current, profiles, plan, today=date(2026, 8, 20)
        )
        setup = yaml.safe_load(candidates["10 Profiles/Setup.yaml"])
        self.assertNotIn("card", setup)


if __name__ == "__main__":
    unittest.main()
