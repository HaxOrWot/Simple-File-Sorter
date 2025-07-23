import json
from pathlib import Path
from core.utils import safe_load_json, safe_save_json

# Global variable to store the workspace path
_workspace_path = None

def set_workspace_path(workspace: Path):
    """Set the workspace path for config file locations."""
    global _workspace_path
    _workspace_path = workspace

def get_config_dir():
    """Get the config directory based on the current workspace."""
    if _workspace_path is None:
        # Fallback to old behavior if no workspace is set
        return Path(__file__).resolve().parent.parent / "config"
    
    # Create config inside FileSorter subfolder of the workspace
    return _workspace_path / "FileSorter" / "config"

def get_built_in_file():
    """Get the built-in categories file path."""
    return get_config_dir() / "built_in_categories.json"

def get_user_file():
    """Get the user categories file path."""
    return get_config_dir() / "user_categories.json"

# -----------------------------------------------------------
# 1.  Generate built_in_categories.json if missing
# -----------------------------------------------------------
def _ensure_built_in_file():
    built_in_file = get_built_in_file()
    if built_in_file.exists():
        return
    
    # Ensure the config directory exists
    built_in_file.parent.mkdir(parents=True, exist_ok=True)
    
    base = {
        "Images":   ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg", "ico", "tiff", "tif"],
        "Videos":   ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v", "3gp", "ogv"],
        "Audio":    ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "opus", "aiff"],
        "Docs":     ["pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "txt", "odt", "odp", "ods", "rtf"],
        "Executable": ["exe", "msi", "dmg", "app", "deb", "rpm", "apk"],
        "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "lz", "zst"],
        "Code":     ["py", "js", "ts", "html", "css", "scss", "cpp", "c", "h", "hpp", "java", "go", "rs", "php", "rb", "swift", "kt", "dart", "json", "xml", "yaml", "yml", "toml"],
        "Fonts":    ["ttf", "otf", "woff", "woff2", "eot"],
        "Ebooks":   ["epub", "mobi", "azw3", "djvu"],
        "Sheets":   ["csv", "tsv"],
        "Other":    []
    }
    safe_save_json(built_in_file, base)

# -----------------------------------------------------------
# 2.  Public API
# -----------------------------------------------------------
def load_categories():
    _ensure_built_in_file()
    built_in_file = get_built_in_file()
    user_file = get_user_file()
    
    built_in = safe_load_json(built_in_file)
    user = safe_load_json(user_file) if user_file.exists() else {}
    merged = built_in.copy()
    merged.update(user)
    return merged

def save_user_categories(new_categories: dict):
    user_file = get_user_file()
    # Ensure the config directory exists
    user_file.parent.mkdir(parents=True, exist_ok=True)
    safe_save_json(user_file, new_categories)

def save_recent_workspace(workspace_path: Path):
    """Save a workspace path to the recent workspaces list."""
    try:
        recent_dir = Path.home() / "AppData" / "Local" / "FileSorter"
        recent_dir.mkdir(parents=True, exist_ok=True)
        
        recent_file = recent_dir / "recent_workspaces.txt"
        
        # Read existing workspaces
        existing = []
        if recent_file.exists():
            existing = recent_file.read_text().strip().split("\n")
        
        # Add current workspace to the top
        workspace_str = str(workspace_path)
        if workspace_str in existing:
            existing.remove(workspace_str)
        existing.insert(0, workspace_str)
        
        # Keep only the 5 most recent
        existing = existing[:5]
        
        # Write back
        recent_file.write_text("\n".join(existing))
    except Exception as e:
        # Just log and continue if we can't save the recent workspace
        import logging
        logging.getLogger('FileSorter').warning(f"Failed to save recent workspace: {e}")