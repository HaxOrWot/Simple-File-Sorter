import json
import os
import tempfile
from pathlib import Path
from core.errors import (
    NoLocationFound, 
    InvalidDirectory, 
    ConfigReadError, 
    ConfigWriteError,
    DuplicateExtension, 
    EmptyExtension, 
    EmptyCategoryName, 
    InvalidExtensionFormat
)

# ---------- Workspace ----------
def ensure_workspace(workspace: Path) -> None:
    if not workspace or not workspace.exists():
        raise NoLocationFound("Please choose a workspace folder first.")
    if not workspace.is_dir():
        raise InvalidDirectory(f"'{workspace}' is not a valid directory.")

# ---------- Config ----------
def safe_load_json(path: Path):
    try:
        return json.loads(path.read_text()) if path.exists() else {}
    except (json.JSONDecodeError, OSError) as e:
        raise ConfigReadError(f"Cannot read config file: {e}") from e

def safe_save_json(path: Path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2))
        tmp_path.replace(path)
    except OSError as e:
        raise ConfigWriteError(f"Cannot write config file: {e}") from e

# ---------- Validation ----------
def validate_extension(ext: str) -> str:
    if not ext or not ext.strip():
        raise EmptyExtension("Extension cannot be empty.")
    ext = ext.lower().lstrip(".")
    if not ext.isalnum():
        raise InvalidExtensionFormat("Extensions must be alphanumeric.")
    return ext

def validate_category_name(name: str) -> str:
    if not name or not name.strip():
        raise EmptyCategoryName("Category name cannot be empty.")
    return name.strip()

