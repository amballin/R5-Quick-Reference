import copy


def merge(base, overrides):
    """Recursively merge profile overrides into baseline defaults."""
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result

