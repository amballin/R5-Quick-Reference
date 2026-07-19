import os
import tempfile
from datetime import datetime
from pathlib import Path

import yaml


class PublishMetadataError(ValueError):
    pass


def load_publish_metadata(path):
    path = Path(path)
    if not path.is_file():
        raise PublishMetadataError(f"Publish metadata file is missing: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PublishMetadataError(f"Could not read publish metadata {path}: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"version", "published"}:
        raise PublishMetadataError("Publish metadata must contain only 'version' and 'published'.")
    version = data["version"]
    if not isinstance(version, dict) or set(version) != {"major", "minor"}:
        raise PublishMetadataError("Publish metadata version must contain major and minor integers.")
    major, minor = version["major"], version["minor"]
    if isinstance(major, bool) or not isinstance(major, int) or major < 0:
        raise PublishMetadataError("Publish metadata major version must be a nonnegative integer.")
    if isinstance(minor, bool) or not isinstance(minor, int) or minor < 0:
        raise PublishMetadataError("Publish metadata minor version must be a nonnegative integer.")
    published = data["published"]
    if isinstance(published, str):
        try:
            published = datetime.fromisoformat(published)
        except ValueError as exc:
            raise PublishMetadataError("Publish timestamp must be a valid ISO 8601 timestamp.") from exc
    if not isinstance(published, datetime) or published.tzinfo is None or published.utcoffset() is None:
        raise PublishMetadataError("Publish timestamp must include a UTC offset.")
    return {"version": {"major": major, "minor": minor}, "published": published}


def next_publish_metadata(current, published=None):
    published = published or datetime.now().astimezone()
    if published.tzinfo is None or published.utcoffset() is None:
        raise PublishMetadataError("Publish timestamp must include a UTC offset.")
    return {
        "version": {"major": current["version"]["major"], "minor": current["version"]["minor"] + 1},
        "published": published,
    }


def display_publish_metadata(metadata):
    version = metadata["version"]
    return f"Version {version['major']}.{version['minor']:02d} • {metadata['published'].strftime('%Y/%m/%d')}"


def write_publish_metadata_atomic(path, metadata):
    path = Path(path)
    content = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
