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
    analyze_my_menu_routes,
    plan_baseline_migration,
)
from html_renderer import field_setup_summary


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

    def test_migration_plan_adds_missing_my_menu_cues_as_profile_changes(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Travel": {
                    "title": "Travel",
                    "card": {
                        "field_setup": {
                            "start": "C3",
                            "source_profile": "Landscape",
                            "my_menus": [],
                        }
                    },
                    "overrides": {},
                }
            },
            [],
            registration(),
            {"shutter.type": "shoot6_shutter_mode"},
            [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["profile_card_cues_to_add"], 1)
        self.assertEqual(
            result["profile_card_cues_to_add"],
            [
                {
                    "profile": "Travel",
                    "title": "Travel",
                    "tab": "SWITCH",
                    "path": "shutter.type",
                    "item_id": "shoot6_shutter_mode",
                    "yaml_path": "card.field_setup.my_menus",
                }
            ],
        )

    def test_migration_plan_adds_cue_without_cx_foundation(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Unregistered": {
                    "title": "Unregistered",
                    "overrides": {},
                }
            },
            [],
            registration(),
            {"shutter.type": "shoot6_shutter_mode"},
            [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["profile_card_cues_to_add"], 1)
        self.assertEqual(result["profile_card_cues_to_add"][0]["profile"], "Unregistered")

    def test_migration_plan_adds_cue_to_profile_based_reference_card(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Setup": {
                    "title": "Setup",
                    "display_category": "reference",
                    "overrides": {},
                }
            },
            [],
            registration(),
            {"shutter.type": "shoot6_shutter_mode"},
            [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}],
        )
        self.assertEqual(result["summary"]["profile_card_cues_to_add"], 1)
        self.assertEqual(result["profile_card_cues_to_add"][0]["profile"], "Setup")

    def test_migration_plan_removes_cue_for_removed_tab(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Travel": {
                    "title": "Travel",
                    "card": {
                        "field_setup": {
                            "my_menus": [{"name": "OLD", "settings": ["shutter.type"]}]
                        }
                    },
                    "overrides": {},
                }
            },
            [],
            registration(),
            {"shutter.type": "shoot6_shutter_mode"},
            [],
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["summary"]["profile_card_cues_to_remove"], 1)
        self.assertEqual(
            result["profile_card_cues_to_remove"][0],
            {
                "profile": "Travel",
                "title": "Travel",
                "tab": "OLD",
                "path": "shutter.type",
                "item_id": "shoot6_shutter_mode",
                "reason": "tab_removed",
                "yaml_path": "card.field_setup.my_menus",
            },
        )

    def test_migration_plan_moves_cue_when_tab_is_renamed(self):
        result = plan_baseline_migration(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {
                "Travel": {
                    "title": "Travel",
                    "card": {
                        "field_setup": {
                            "my_menus": [{"name": "OLD", "settings": ["shutter.type"]}]
                        }
                    },
                    "overrides": {},
                }
            },
            [],
            registration(),
            {"shutter.type": "shoot6_shutter_mode"},
            [{"name": "NEW", "items": ["shoot6_shutter_mode"]}],
        )
        self.assertEqual(result["summary"]["profile_card_cues_to_remove"], 1)
        self.assertEqual(result["summary"]["profile_card_cues_to_add"], 1)
        self.assertEqual(result["profile_card_cues_to_remove"][0]["tab"], "OLD")
        self.assertEqual(result["profile_card_cues_to_add"][0]["tab"], "NEW")

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

    def test_my_menu_assignment_remains_displayed_when_start_and_target_match(self):
        result = analyze_my_menu_routes(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "Mechanical"}),
            {
                "People": {
                    "title": "People",
                    "card": {
                        "field_setup": {
                            "start": "C1",
                            "source_profile": "Wildlife",
                            "my_menus": [
                                {"name": "SWITCH", "settings": ["shutter.type"]}
                            ],
                        }
                    },
                    "overrides": {},
                }
            },
            registration(c1="Mechanical"),
            {"shutter.type": "shoot6_shutter_mode"},
            [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}],
        )
        profile = result["profiles"][0]
        assignment = profile["declared_settings"][0]
        self.assertTrue(assignment["displayed_before"])
        self.assertTrue(assignment["displayed_after"])
        self.assertTrue(profile["tabs"][0]["shown_on_card"])
        self.assertEqual(result["summary"]["displayed_assignments"], 1)
        self.assertEqual(result["summary"]["hidden_assignments"], 0)

    def test_my_menu_route_reports_displayed_item_missing_from_named_tab(self):
        result = analyze_my_menu_routes(
            baseline(autofocus={"subject_detection": "Animals"}),
            baseline(autofocus={"subject_detection": "Animals"}),
            {
                "People": {
                    "title": "People",
                    "card": {
                        "field_setup": {
                            "start": "C1",
                            "my_menus": [
                                {
                                    "name": "SWITCH",
                                    "settings": ["autofocus.subject_detection"],
                                }
                            ],
                        }
                    },
                    "overrides": {"autofocus": {"subject_detection": "People"}},
                }
            },
            registration(),
            {"autofocus.subject_detection": "af1_subject_to_detect"},
            [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}],
        )
        assignment = result["profiles"][0]["declared_settings"][0]
        self.assertTrue(assignment["displayed_after"])
        self.assertTrue(assignment["tab_present"])
        self.assertFalse(assignment["item_available"])
        self.assertTrue(assignment["availability_problem"])
        self.assertTrue(assignment["obsolete"])
        self.assertEqual(assignment["reason"], "shortcut_removed")
        self.assertEqual(result["summary"]["unavailable_settings"], 1)
        self.assertEqual(result["summary"]["obsolete_card_cues"], 1)

    def test_hidden_route_is_obsolete_when_its_tab_is_removed(self):
        result = analyze_my_menu_routes(
            baseline(autofocus={"operation": "One-Shot AF", "servo_af_case": "Case A (Auto)"}),
            baseline(autofocus={"operation": "One-Shot AF", "servo_af_case": "Case A (Auto)"}),
            {
                "Travel": {
                    "title": "Travel",
                    "card": {
                        "field_setup": {
                            "my_menus": [
                                {"name": "AF Case", "settings": ["autofocus.servo_af_case"]}
                            ]
                        }
                    },
                    "overrides": {},
                }
            },
            registration(),
            {"autofocus.servo_af_case": "af3_servo_af_characteristics"},
            [],
        )
        profile = result["profiles"][0]
        self.assertFalse(profile["declared_settings"][0]["displayed_after"])
        self.assertEqual(
            profile["obsolete_card_cues"],
            [{
                "tab": "AF Case",
                "path": "autofocus.servo_af_case",
                "item_id": "af3_servo_af_characteristics",
                "reason": "tab_removed",
            }],
        )
        self.assertEqual(profile["warning_count"], 1)

    def test_my_menu_route_reports_newly_visible_setting_without_card_cue(self):
        result = analyze_my_menu_routes(
            baseline(autofocus={"operation": "One-Shot AF", "servo_af_case": "Case A (Auto)"}),
            baseline(autofocus={"operation": "Servo AF", "servo_af_case": "Case A (Auto)"}),
            {
                "Travel": {
                    "title": "Travel",
                    "card": {"field_setup": {"start": "C1", "my_menus": []}},
                    "overrides": {},
                }
            },
            registration(),
            {"autofocus.servo_af_case": "af3_servo_af_characteristics"},
            [{"name": "AF Case", "items": ["af3_servo_af_characteristics"]}],
        )
        missing = result["profiles"][0]["missing_card_cues"][0]
        self.assertEqual(missing["path"], "autofocus.servo_af_case")
        self.assertTrue(missing["newly_visible"])
        self.assertEqual(missing["available_in_tabs"], ["AF Case"])
        self.assertEqual(result["summary"]["newly_visible_missing_cues"], 1)

    def test_direct_control_does_not_create_missing_card_cue(self):
        result = analyze_my_menu_routes(
            baseline(exposure={"mode": "Fv"}),
            baseline(exposure={"mode": "Fv"}),
            {
                "Sports": {
                    "title": "Sports",
                    "card": {"field_setup": {"start": "C1"}},
                    "overrides": {"exposure": {"mode": "Tv"}},
                }
            },
            registration(),
            {},
            [],
        )
        self.assertEqual(result["profiles"], [])
        self.assertEqual(result["summary"]["missing_card_cues"], 0)

    def test_only_configured_shortcuts_unused_by_all_cards_are_flagged(self):
        result = analyze_my_menu_routes(
            baseline(shutter={"type": "EFCS"}),
            baseline(shutter={"type": "EFCS"}),
            {"Travel": {"title": "Travel", "card": {}, "overrides": {}}},
            registration(),
            {
                "shutter.type": "shoot6_shutter_mode",
                "image.focus_bracketing": "shoot5_focus_bracketing",
            },
            [
                {
                    "name": "SWITCH",
                    "items": ["shoot6_shutter_mode", "shoot5_focus_bracketing"],
                }
            ],
        )
        self.assertEqual(
            result["unreferenced_configured_items"],
            [
                {
                    "item_id": "shoot5_focus_bracketing",
                    "path": "image.focus_bracketing",
                    "tabs": ["SWITCH"],
                }
            ],
        )

    def test_card_renderer_omits_only_menu_tabs_without_visible_settings(self):
        profile = {
            "title": "People",
            "card": {
                "field_setup": {
                    "start": "C1",
                    "my_menus": [
                        {
                            "name": "AF Case",
                            "settings": [
                                "autofocus.servo_af_case",
                                "autofocus.switching_tracked_subjects",
                            ],
                        }
                    ],
                }
            },
            "overrides": {},
        }
        merged = {
            "autofocus": {
                "operation": "One-Shot AF",
                "servo_af_case": "Case A (Auto)",
                "method": "Face + Tracking",
                "switching_tracked_subjects": "On subject",
            }
        }
        summary = field_setup_summary(profile, merged)
        self.assertEqual(summary["menus"][0]["name"], "AF Case")
        self.assertEqual(
            summary["menus"][0]["settings"],
            ["autofocus.switching_tracked_subjects"],
        )

        merged["autofocus"]["method"] = "1-Point AF"
        self.assertEqual(field_setup_summary(profile, merged)["menus"], [])

    def test_my_menu_route_analysis_does_not_mutate_inputs(self):
        current = baseline(shutter={"type": "EFCS"})
        proposed = baseline(shutter={"type": "Mechanical"})
        profiles = {
            "Travel": {
                "title": "Travel",
                "card": {"field_setup": {"start": "C1"}},
                "overrides": {},
            }
        }
        source = registration(c1="EFCS")
        identities = {"shutter.type": "shoot6_shutter_mode"}
        tabs = [{"name": "SWITCH", "items": ["shoot6_shutter_mode"]}]
        before = deepcopy((current, proposed, profiles, source, identities, tabs))
        analyze_my_menu_routes(current, proposed, profiles, source, identities, tabs)
        self.assertEqual((current, proposed, profiles, source, identities, tabs), before)


if __name__ == "__main__":
    unittest.main()
