# --- Configuration File Paths and Names ---
SORT_DEST_FILE = 'sort_dest.txt' # Stores the main sorting destination path
DROP_LOCATION_FILE = 'drop_dest.txt' # Stores the parent directory path for the 'Drop' folder
CATEGORIES_FILE = 'categories.json' # Stores defined file categories
EXTENSIONS_FILE = 'extensions.json' # Stores file extensions mapped to categories
DROP_FOLDER_NAME = 'Drop' # The exact name of the folder where files are placed for sorting (case-sensitive)
UNSORTED_FOLDER_NAME = 'Unsorted' # Name of the folder for files with unknown extensions
ASST_FOLDER = 'asst' # Name of the subfolder for JSON configuration files
APP_BASE_PATH_MARKER = 'app_base_path.txt' # Marker file to store the chosen permanent base directory for the app's configs

# --- Default Configurations (Used if JSON files don't exist or are corrupted) ---
DEFAULT_CATEGORIES = ["Video", "Music", "Code", "Image", "Document", "Archive", "Executable", "Other"]

DEFAULT_EXTENSIONS = {
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".alac"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".swift", ".kt", ".json", ".xml", ".yml", ".yaml", ".sh", ".bat", ".ps1", ".md"],
    "Image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico", ".raw", ".heif", ".heic"],
    "Document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt", ".ods", ".odp", ".csv", ".epub", ".mobi"],
    "Archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "Executable": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".apk"],
    "Other": []
}
