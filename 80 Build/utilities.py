def flatten(data, prefix=""):
    """Flatten nested dictionaries into dot-separated keys."""
    output = {}
    if not isinstance(data, dict):
        return output
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            output.update(flatten(value, name))
        else:
            output[name] = value
    return output

