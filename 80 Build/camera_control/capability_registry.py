"""Load the canonical EOS R5 property set for read-only discovery."""

from pathlib import Path

import yaml


CATALOG_PATH = Path(__file__).resolve().parents[2] / "00 Master" / "camera_capabilities.yaml"


def load_capability_properties():
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    return tuple(
        (
            item["key"],
            item["label"],
            int(item["edsdk_property_id"]),
            int(item["simulated_value_raw"]),
        )
        for item in catalog["properties"]
    )


CAPABILITY_PROPERTIES = load_capability_properties()


def simulated_capabilities(values=None):
    values = values or {}
    properties = []
    unreadable_errors = {"noise_reduction": 80, "subject_detection": 7}
    for key, label, property_id, default_value in CAPABILITY_PROPERTIES:
        value = values.get(key, default_value)
        is_readable = key not in unreadable_errors
        properties.append(
            {
                "key": key,
                "label": label,
                "property_id": property_id,
                "property_id_hex": f"0x{property_id:08x}",
                "read_status": "sdk_verified" if is_readable else "unreadable",
                "read_error": None if is_readable else unreadable_errors[key],
                "data_type": "uint32" if is_readable else "other",
                "data_type_raw": 9 if is_readable else 0,
                "size": 4 if is_readable else 0,
                "value_raw": value if is_readable else None,
                "value_hex": int(value).to_bytes(4, "little").hex() if is_readable else None,
                "descriptor_status": "sdk_verified",
                "descriptor_error": None,
                "descriptor_access": "read_write" if is_readable else "read",
                "descriptor_access_raw": 2 if is_readable else 0,
                "descriptor_form": 2 if is_readable else 0,
                "allowed_values_raw": [value] if is_readable else [],
                "write_tested": False,
            }
        )
    return properties
