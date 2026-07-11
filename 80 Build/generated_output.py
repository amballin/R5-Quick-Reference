import os
import shutil
import time


def fresh_copy(source, target, ignore=None):
    """Replace a generated output folder with a clean copy."""
    mirror_tree(source, target, ignore=ignore)


def mirror_tree(source, target, ignore=None):
    """Make target match source without replacing the target directory itself."""
    ignored = _ignored_names(source, ignore)
    target.mkdir(parents=True, exist_ok=True)
    source_paths = {
        path.relative_to(source)
        for path in source.rglob("*")
        if not _is_ignored(path, source, ignored)
    }

    for path in sorted(target.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        relative = path.relative_to(target)
        if path.name == ".DS_Store" or relative not in source_paths:
            _remove_path(path)

    for relative in sorted(source_paths):
        source_path = source / relative
        target_path = target / relative
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if not target_path.exists() or target_path.read_bytes() != source_path.read_bytes():
                shutil.copy2(source_path, target_path)
    clean_generated_tree(target)


def _ignored_names(source, ignore):
    return set(ignore(source, os.listdir(source)) if ignore and source.exists() else [])


def _is_ignored(path, source, ignored):
    return any(part in ignored or part == ".DS_Store" or part == "__pycache__" for part in path.relative_to(source).parts)


def _remove_path(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def clean_generated_tree(root):
    for attempt in range(5):
        remove_numbered_duplicates(root, require_original=False)
        remove_ds_store(root)
        if not numbered_duplicates(root, require_original=False) and not ds_store_files(root):
            return
        if attempt < 4:
            time.sleep(0.2)


def remove_ds_store(root):
    for path in ds_store_files(root):
        if path.is_file():
            path.unlink()


def ds_store_files(root):
    if not root.exists():
        return []
    return list(root.rglob(".DS_Store"))


def numbered_duplicates(root, require_original=True):
    """Return Finder-style duplicate paths that have an unsuffixed original."""
    if not root.exists():
        return []
    duplicates = []
    for parent_name, dirnames, filenames in os.walk(root, topdown=False):
        parent = root.__class__(parent_name)
        for name in dirnames + filenames:
            path = parent / name
            original = unsuffixed_original(path)
            if original and (not require_original or original.exists()):
                duplicates.append(path)
    return sorted(duplicates, key=lambda item: len(item.parts), reverse=True)


def remove_numbered_duplicates(root, require_original=True):
    for duplicate in numbered_duplicates(root, require_original=require_original):
        if duplicate.is_dir():
            shutil.rmtree(duplicate)
        elif duplicate.exists():
            duplicate.unlink()


def unsuffixed_original(path):
    suffix = path.suffix if path.is_file() else ""
    stem = path.name[: -len(suffix)] if suffix else path.name
    base, separator, number = stem.rpartition(" ")
    if not separator or not base or not number.isdigit():
        return None
    return path.with_name(f"{base}{suffix}")
