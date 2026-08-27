"""Load, validate, and evaluate canonical Canon feature-interaction rules."""

from __future__ import annotations

from pathlib import Path

import yaml

from utilities import flatten


CATALOG = Path("00 Master") / "feature_interactions.yaml"
OPERATORS = {"equals", "not_equals", "in", "not_in", "exists"}
EVIDENCE_CLASSES = {
    "verified_canon_capability",
    "owner_confirmed_current_configuration",
    "approved_target_pending_physical_verification",
    "project_recommendation",
    "unresolved_item",
}
BEHAVIORS = {"inactive", "restricted", "replaced", "overridden", "coordinated", "available", "automatic"}
SURFACES = {"card", "editor", "camera_lab"}


class FeatureInteractionError(ValueError):
    """Raised when the canonical interaction catalog is invalid."""


def load_catalog(root):
    path = Path(root) / CATALOG
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise FeatureInteractionError(f"Feature-interaction catalog could not be read: {exc}") from exc
    errors = validate_catalog(data)
    if errors:
        raise FeatureInteractionError("; ".join(errors))
    return data


def validate_catalog(data, known_setting_paths=None):
    errors = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["Catalog must be a mapping with schema_version 1."]
    if data.get("camera") != {"manufacturer": "Canon", "model": "EOS R5"}:
        errors.append("Catalog must target Canon EOS R5 exactly.")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        return errors + ["Catalog must define a non-empty rules list."]
    ids = set()
    for index, rule in enumerate(rules, start=1):
        label = f"Rule {index}"
        if not isinstance(rule, dict):
            errors.append(f"{label} must be a mapping.")
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            errors.append(f"{label} requires a non-empty id.")
        elif rule_id in ids:
            errors.append(f"Duplicate rule id: {rule_id}.")
        else:
            ids.add(rule_id)
            label = rule_id
        if rule.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{label}: invalid evidence_class.")
        conditions = (rule.get("when") or {}).get("all")
        if not isinstance(conditions, list) or not conditions:
            errors.append(f"{label}: when.all must be a non-empty list.")
            conditions = []
        for condition in conditions:
            errors.extend(_validate_condition(label, condition, known_setting_paths))
        requirements = rule.get("context_requirements") or []
        if not isinstance(requirements, list) or any(
            not isinstance(path, str) or not path.startswith("context.") for path in requirements
        ):
            errors.append(f"{label}: context_requirements must contain only context.* paths.")
        effects = rule.get("effects")
        if not isinstance(effects, list) or not effects:
            errors.append(f"{label}: effects must be a non-empty list.")
            effects = []
        for effect in effects:
            if not isinstance(effect, dict) or effect.get("behavior") not in BEHAVIORS:
                errors.append(f"{label}: every effect requires a supported behavior.")
                continue
            setting_paths = effect.get("setting_paths")
            if not isinstance(setting_paths, list) or not setting_paths:
                errors.append(f"{label}: every effect requires setting_paths.")
            elif known_setting_paths is not None:
                for path in setting_paths:
                    if path not in known_setting_paths:
                        errors.append(f"{label}: unknown effect setting path {path}.")
        if not isinstance(rule.get("message"), str) or not rule.get("message", "").strip():
            errors.append(f"{label}: message is required.")
        surfaces = rule.get("surfaces")
        if not isinstance(surfaces, list) or not surfaces or any(item not in SURFACES for item in surfaces):
            errors.append(f"{label}: surfaces must contain supported surface names.")
        sources = rule.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}: at least one Canon source is required.")
        else:
            for source in sources:
                if not isinstance(source, dict) or not source.get("title") or not str(source.get("url", "")).startswith("https://"):
                    errors.append(f"{label}: every source requires a title and HTTPS URL.")
    return errors


def _validate_condition(label, condition, known_setting_paths):
    if not isinstance(condition, dict):
        return [f"{label}: every condition must be a mapping."]
    path = condition.get("path")
    operator = condition.get("operator")
    errors = []
    if not isinstance(path, str) or not path:
        errors.append(f"{label}: every condition requires a path.")
    elif known_setting_paths is not None and not path.startswith("context.") and path not in known_setting_paths:
        errors.append(f"{label}: unknown condition setting path {path}.")
    if operator not in OPERATORS:
        errors.append(f"{label}: unsupported operator {operator}.")
    elif operator in {"in", "not_in"} and not isinstance(condition.get("values"), list):
        errors.append(f"{label}: {operator} requires values.")
    elif operator in {"equals", "not_equals"} and "value" not in condition:
        errors.append(f"{label}: {operator} requires value.")
    elif operator == "exists" and "value" in condition and not isinstance(condition["value"], bool):
        errors.append(f"{label}: exists value must be true or false when supplied.")
    return errors


def evaluate(settings, catalog, context=None, surface=None):
    """Return matched rules without inferring absent settings or equipment context."""
    values = flatten(settings) if isinstance(settings, dict) else dict(settings or {})
    context_values = flatten(context) if isinstance(context, dict) else dict(context or {})
    values.update({f"context.{key}": value for key, value in context_values.items()})
    findings = []
    for rule in catalog.get("rules") or []:
        if surface is not None and surface not in rule.get("surfaces", []):
            continue
        requirements = rule.get("context_requirements") or []
        if any(path not in values for path in requirements):
            continue
        conditions = (rule.get("when") or {}).get("all") or []
        if all(_matches(condition, values) for condition in conditions):
            findings.append(rule)
    return findings


def _matches(condition, values):
    path = condition["path"]
    operator = condition["operator"]
    present = path in values
    if operator == "exists":
        return present is condition.get("value", True)
    if not present:
        return False
    actual = values[path]
    if operator == "equals":
        return actual == condition["value"]
    if operator == "not_equals":
        return actual != condition["value"]
    if operator == "in":
        return actual in condition["values"]
    if operator == "not_in":
        return actual not in condition["values"]
    return False


def interaction_notes(root, settings, surface="card", context=None):
    return [
        rule["message"]
        for rule in evaluate(settings, load_catalog(root), context=context, surface=surface)
    ]
