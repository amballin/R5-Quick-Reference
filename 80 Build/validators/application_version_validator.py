from application_version import ApplicationVersionError, application_version_info

from .common import error


def validate(root):
    try:
        application_version_info(root)
    except ApplicationVersionError as exc:
        return [error("application_version", root / "00 Master/application_version.yaml", str(exc))]
    return []
