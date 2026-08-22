#!/usr/bin/env python3
"""Tests for immutable card identity and structured references."""

from pathlib import Path
import sys
import unittest
from uuid import UUID


BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from migrate_card_ids import migrate
from profile_loader import load_yaml
from validators import card_identity_validator


class CardIdentityTests(unittest.TestCase):
    def test_all_active_cards_have_unique_canonical_uuids_and_valid_references(self):
        ids = []
        for path in sorted((PROJECT_ROOT / "10 Profiles").glob("*.yaml")):
            card_id = load_yaml(path).get("card_id")
            self.assertEqual(str(UUID(card_id)), card_id)
            ids.append(card_id)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(card_identity_validator.validate(PROJECT_ROOT), [])

    def test_legacy_migration_is_idempotent_after_conversion(self):
        self.assertEqual(migrate(PROJECT_ROOT, apply=False), [])


if __name__ == "__main__":
    unittest.main()
