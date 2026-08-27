import yaml

from .common import error


CATALOG = "00 Master/camera_capabilities.yaml"


def validate(root):
    path = root / CATALOG
    if not path.is_file():
        return [error("camera_capabilities", path, "Capability catalog is missing.")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [error("camera_capabilities", path, f"Capability catalog could not be read: {exc}")]
    issues = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return [error("camera_capabilities", path, "Capability catalog must use schema_version 1.")]
    camera = data.get("camera") or {}
    if camera != {"manufacturer": "Canon", "model": "EOS R5"}:
        issues.append(error("camera_capabilities", path, "Capability catalog must target Canon EOS R5 exactly."))
    policy = data.get("write_policy") or {}
    if policy.get("enabled") is not False or policy.get("descriptor_is_write_proof") is not False:
        issues.append(error("camera_capabilities", path, "Capability writes and descriptor-as-proof must remain disabled."))

    properties = data.get("properties")
    if not isinstance(properties, list) or not properties:
        return issues + [error("camera_capabilities", path, "Capability catalog must define properties.")]
    keys = [item.get("key") for item in properties if isinstance(item, dict)]
    property_ids = [item.get("edsdk_property_id") for item in properties if isinstance(item, dict)]
    if len(keys) != len(properties) or any(not isinstance(key, str) or not key for key in keys):
        issues.append(error("camera_capabilities", path, "Every capability property requires a non-empty key."))
    if len(set(keys)) != len(keys):
        issues.append(error("camera_capabilities", path, "Capability property keys must be unique."))
    if any(not isinstance(value, int) for value in property_ids) or len(set(property_ids)) != len(property_ids):
        issues.append(error("camera_capabilities", path, "EDSDK property IDs must be unique integers."))
    valid_classifications = {"sdk_readable", "conditional", "context_only"}
    for item in properties:
        if item.get("capability_classification") not in valid_classifications:
            issues.append(error("camera_capabilities", path, f"Invalid capability classification: {item.get('key')}"))
        if not isinstance(item.get("profile_paths"), list) or not isinstance(item.get("dependencies"), list):
            issues.append(error("camera_capabilities", path, f"Capability mapping metadata is incomplete: {item.get('key')}"))

    if _contains_key(data, "body_id"):
        issues.append(error("camera_capabilities", path, "Tracked capability evidence must not contain a camera body ID."))
    for observation in data.get("observations") or []:
        if observation.get("evidence_method") != "sdk_verified":
            issues.append(error("camera_capabilities", path, "Physical observations must use sdk_verified evidence."))
        if observation.get("read_only") is not True or observation.get("write_testing_performed") is not False:
            issues.append(error("camera_capabilities", path, "Capability observations must remain read-only."))
        observed_properties = observation.get("properties") or []
        observed_keys = [item.get("key") for item in observed_properties if isinstance(item, dict)]
        if set(observed_keys) != set(keys):
            issues.append(error("camera_capabilities", path, "Every observation must cover the complete reviewed property set."))
        for item in observed_properties:
            if item.get("write_classification") != "unverified":
                issues.append(error("camera_capabilities", path, "Real-camera write classifications must remain unverified during simulator-only Phase 2A."))
    return issues


def _contains_key(value, prohibited):
    if isinstance(value, dict):
        return prohibited in value or any(_contains_key(child, prohibited) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(child, prohibited) for child in value)
    return False
