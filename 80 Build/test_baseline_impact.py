#!/usr/bin/env python3
"""Unit tests for read-only baseline impact analysis."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest


BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from baseline_impact import (
    BaselineImpactError,
    analyze_baseline_impact,
    analyze_cx_impact,
    plan_baseline_migration,
)


def baseline(**defaults):
    return {"defaults": defaults}


def registration(**row_values):
    row = {"setting": "Shutter Type", "baseline_key": "shutter.type"}
    row.update(row_values)
    return {
        "profiles": [
            {"key": "c1", "heading": "C1 Wildlife"},
            {"key": "c2", "heading": "C2 Birds in Flight"},
            {"key": "c3", "heading": "C3 Landscape"},
        ],
        "rows": [row],
    }


class BaselineImpactTests(unittest.TestCase):
    def test_reports_no_impact_when_baseline_is_unchanged(self):
        current = baseline(drive={"mode": "Single Shot"})
        result = analyze_baseline_impact(current, deepcopy(current), {})
        self.assertEqual(result["summary"]["changed_settings"], 0)
        self.assertEqual(result["changes"], [])

    def test_inherited_value_requires_explicit_decision(self):
        result = analyze_baseline_impact(
            baseline(drive={"mode": "Single Shot"}),
            baseline(drive={"mode": "High Speed Continuous"}),
            {"Travel": {"title": "Travel", "inherits": "baseline", "overrides": {}}},
        )
        impact = result["changes"][0]["profiles"][0]
        self.assertEqual(impact["classification"], "inherited_change")
        self.assertEqual(impact["old_effective_value"], "Single Shot")
        self.assertEqual(impact["new_effective_value"], "High Speed Continuous")
        self.assertTrue(impact["requires_decision"])
        self.assertEqual(impact["recommended_action"], "review_baseline_change")

    def test_existing_override_protects_profile_value(self):
        result = analyze_baseline_impact(
            baseline(shutter={"type": "Mechanical"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "People": {
                    "title": "People",
                    "inherits": "baseline",
                    "overrides": {"shutter": {"type": "Electronic"}},
                }
            },
        )
        impact = result["changes"][0]["profiles"][0]
        self.assertEqual(impact["classification"], "override_protected")
        self.assertEqual(impact["old_effective_value"], "Electronic")
        self.assertEqual(impact["new_effective_value"], "Electronic")
        self.assertFalse(impact["requires_decision"])

    def test_override_matching_proposed_baseline_is_redundant(self):
        result = analyze_baseline_impact(
            baseline(shutter={"type": "Mechanical"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Wildlife": {
                    "title": "Wildlife",
                    "inherits": "baseline",
                    "overrides": {"shutter": {"type": "EFCS"}},
                }
            },
        )
        impact = result["changes"][0]["profiles"][0]
        self.assertEqual(impact["classification"], "override_redundant")
        self.assertEqual(impact["recommended_action"], "remove_override")
        self.assertEqual(impact["old_effective_value"], impact["new_effective_value"])

    def test_removed_path_marks_existing_override_invalid(self):
        result = analyze_baseline_impact(
            baseline(display={"histogram": "RGB"}),
            baseline(display={}),
            {
                "Landscape": {
                    "title": "Landscape",
                    "inherits": "baseline",
                    "overrides": {"display": {"histogram": "Brightness"}},
                }
            },
        )
        change = result["changes"][0]
        impact = change["profiles"][0]
        self.assertEqual(change["change_type"], "removed")
        self.assertEqual(impact["classification"], "override_invalid_path")
        self.assertTrue(impact["requires_decision"])

    def test_type_change_marks_incompatible_override_invalid(self):
        result = analyze_baseline_impact(
            baseline(exposure={"maximum": 12800}),
            baseline(exposure={"maximum": "12800"}),
            {
                "Sports": {
                    "title": "Sports",
                    "inherits": "baseline",
                    "overrides": {"exposure": {"maximum": 6400}},
                }
            },
        )
        change = result["changes"][0]
        impact = change["profiles"][0]
        self.assertEqual(change["change_type"], "type_changed")
        self.assertEqual(impact["classification"], "override_invalid_type")

    def test_added_path_is_visible_for_every_inheriting_profile(self):
        result = analyze_baseline_impact(
            baseline(autofocus={}),
            baseline(autofocus={"touch_drag_af": "Enable"}),
            {
                "Wildlife": {"title": "Wildlife", "inherits": "baseline", "overrides": {}},
                "Camera Buttons": {
                    "title": "Camera Buttons",
                    "card_type": "reference",
                    "reference_settings": [],
                },
            },
        )
        self.assertEqual(result["changes"][0]["change_type"], "added")
        self.assertEqual(result["changes"][0]["profiles"][0]["name"], "Wildlife")
        self.assertEqual(result["skipped_reference_cards"], ["Camera Buttons"])
        self.assertEqual(result["summary"]["reference_cards_skipped"], 1)

    def test_efcs_scenario_separates_inherited_protected_and_redundant_profiles(self):
        result = analyze_baseline_impact(
            baseline(shutter={"type": "Mechanical"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Travel": {"title": "Travel", "inherits": "baseline", "overrides": {}},
                "People": {
                    "title": "People",
                    "inherits": "baseline",
                    "overrides": {"shutter": {"type": "Electronic"}},
                },
                "Wildlife": {
                    "title": "Wildlife",
                    "inherits": "baseline",
                    "overrides": {"shutter": {"type": "EFCS"}},
                },
            },
        )
        classifications = result["summary"]["classifications"]
        self.assertEqual(classifications["inherited_change"], 1)
        self.assertEqual(classifications["override_protected"], 1)
        self.assertEqual(classifications["override_redundant"], 1)
        self.assertEqual(result["summary"]["affected_profiles"], 2)
        self.assertEqual(result["summary"]["profiles_requiring_decision"], 1)

    def test_inputs_are_not_mutated(self):
        current = baseline(shutter={"type": "Mechanical"})
        proposed = baseline(shutter={"type": "EFCS"})
        profiles = {"Travel": {"title": "Travel", "overrides": {}}}
        before = deepcopy((current, proposed, profiles))
        analyze_baseline_impact(current, proposed, profiles)
        self.assertEqual((current, proposed, profiles), before)

    def test_rejects_missing_defaults(self):
        with self.assertRaisesRegex(BaselineImpactError, "defaults must be a mapping"):
            analyze_baseline_impact({}, baseline(), {})

    def test_migration_plan_requires_an_explicit_inherited_decision(self):
        result = plan_baseline_migration(
            baseline(drive={"mode": "Single Shot"}),
            baseline(drive={"mode": "High Speed Continuous"}),
            {"Travel": {"title": "Travel", "overrides": {}}},
            [],
        )
        self.assertFalse(result["complete"])
        self.assertEqual(result["summary"]["unresolved_decisions"], 1)
        self.assertEqual(result["unresolved_decisions"][0]["reason"], "decision_required")

    def test_follow_decision_plans_profile_to_follow_without_an_override(self):
        result = plan_baseline_migration(
            baseline(drive={"mode": "Single Shot"}),
            baseline(drive={"mode": "High Speed Continuous"}),
            {"Travel": {"title": "Travel", "overrides": {}}},
            [{"profile": "Travel", "path": "drive.mode", "decision": "follow_baseline"}],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["profiles_following_baseline"], 1)
        self.assertEqual(result["overrides_to_add"], [])

    def test_preserve_decision_plans_previous_value_as_new_override(self):
        result = plan_baseline_migration(
            baseline(drive={"mode": "Single Shot"}),
            baseline(drive={"mode": "High Speed Continuous"}),
            {"Travel": {"title": "Travel", "overrides": {}}},
            [{"profile": "Travel", "path": "drive.mode", "decision": "preserve_previous"}],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["overrides_to_add"][0]["override_value"], "Single Shot")

    def test_redundant_override_is_planned_for_removal(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "Mechanical"}),
            baseline(shutter={"type": "EFCS"}),
            {"Wildlife": {"title": "Wildlife", "overrides": {"shutter": {"type": "EFCS"}}}},
            [],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["overrides_to_remove"], 1)
        self.assertEqual(result["overrides_to_remove"][0]["profile"], "Wildlife")

    def test_invalid_override_keeps_plan_unresolved(self):
        result = plan_baseline_migration(
            baseline(display={"histogram": "RGB"}),
            baseline(display={}),
            {"Landscape": {"title": "Landscape", "overrides": {"display": {"histogram": "Brightness"}}}},
            [],
        )
        self.assertFalse(result["complete"])
        self.assertEqual(result["unresolved_decisions"][0]["reason"], "override_invalid_path")

    def test_rejects_stale_duplicate_and_invalid_decisions(self):
        current = baseline(drive={"mode": "Single Shot"})
        proposed = baseline(drive={"mode": "Continuous"})
        profiles = {"Travel": {"title": "Travel", "overrides": {}}}
        with self.assertRaisesRegex(BaselineImpactError, "Stale or inapplicable"):
            plan_baseline_migration(
                current,
                proposed,
                profiles,
                [{"profile": "Unknown", "path": "drive.mode", "decision": "follow_baseline"}],
            )
        duplicate = {"profile": "Travel", "path": "drive.mode", "decision": "follow_baseline"}
        with self.assertRaisesRegex(BaselineImpactError, "Duplicate"):
            plan_baseline_migration(current, proposed, profiles, [duplicate, duplicate])
        with self.assertRaisesRegex(BaselineImpactError, "Invalid baseline migration decision"):
            plan_baseline_migration(
                current,
                proposed,
                profiles,
                [{"profile": "Travel", "path": "drive.mode", "decision": "maybe"}],
            )

    def test_migration_planning_does_not_mutate_inputs(self):
        current = baseline(drive={"mode": "Single Shot"})
        proposed = baseline(drive={"mode": "Continuous"})
        profiles = {"Travel": {"title": "Travel", "overrides": {}}}
        decisions = [{"profile": "Travel", "path": "drive.mode", "decision": "follow_baseline"}]
        before = deepcopy((current, proposed, profiles, decisions))
        plan_baseline_migration(current, proposed, profiles, decisions)
        self.assertEqual((current, proposed, profiles, decisions), before)

    def test_cx_impact_distinguishes_inherited_and_registration_protected_values(self):
        result = analyze_cx_impact(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "Mechanical"}),
            {
                "Wildlife": {
                    "title": "Wildlife",
                    "card": {"field_setup": {"start": "C1", "source_profile": "Wildlife"}},
                },
                "Sports": {
                    "title": "Sports",
                    "card": {"field_setup": {"start": "C2", "source_profile": "Birds in Flight"}},
                },
                "Landscape": {
                    "title": "Landscape",
                    "card": {"field_setup": {"start": "C3", "source_profile": "Landscape"}},
                },
            },
            registration(c2="Mechanical"),
        )
        modes = {mode["start"]: mode for mode in result["registered_modes"]}
        self.assertTrue(modes["C1"]["affected"])
        self.assertEqual(modes["C1"]["settings"][0]["current_effective_value"], "EFCS")
        self.assertEqual(modes["C1"]["settings"][0]["proposed_effective_value"], "Mechanical")
        self.assertFalse(modes["C2"]["affected"])
        self.assertTrue(modes["C2"]["settings"][0]["registration_override"])
        self.assertEqual(modes["C2"]["settings"][0]["current_effective_value"], "Mechanical")
        self.assertEqual(modes["C2"]["settings"][0]["proposed_effective_value"], "Mechanical")
        self.assertTrue(modes["C3"]["affected"])
        self.assertEqual(
            [warning["title"] for warning in result["route_warnings"]],
            ["Landscape", "Wildlife"],
        )
        self.assertEqual(result["summary"]["affected_registered_modes"], 2)
        self.assertEqual(result["summary"]["profiles_with_affected_starting_mode"], 2)

    def test_cx_impact_reports_every_changed_baseline_setting_per_mode(self):
        result = analyze_cx_impact(
            baseline(shutter={"type": "EFCS"}, drive={"mode": "Single Shot"}),
            baseline(shutter={"type": "Mechanical"}, drive={"mode": "Continuous"}),
            {},
            registration(c2="Mechanical"),
        )
        self.assertEqual(
            [setting["path"] for setting in result["registered_modes"][0]["settings"]],
            ["drive.mode", "shutter.type"],
        )
        self.assertEqual(result["summary"]["effective_setting_changes"], 5)

    def test_cx_impact_rejects_missing_registered_mode_definitions(self):
        with self.assertRaisesRegex(BaselineImpactError, "profiles are missing: c2, c3"):
            analyze_cx_impact(
                baseline(shutter={"type": "EFCS"}),
                baseline(shutter={"type": "Mechanical"}),
                {},
                {"profiles": [{"key": "c1", "heading": "C1 Wildlife"}], "rows": []},
            )

    def test_cx_impact_does_not_mutate_inputs(self):
        current = baseline(shutter={"type": "EFCS"})
        proposed = baseline(shutter={"type": "Mechanical"})
        profiles = {"Wildlife": {"title": "Wildlife", "card": {"field_setup": {"start": "C1"}}}}
        source = registration(c2="Mechanical")
        before = deepcopy((current, proposed, profiles, source))
        analyze_cx_impact(current, proposed, profiles, source)
        self.assertEqual((current, proposed, profiles, source), before)


if __name__ == "__main__":
    unittest.main()
