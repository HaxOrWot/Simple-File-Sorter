class FileSorterError(Exception):
    """Base-class for all FileSorter-specific errors."""
    pass


class NoLocationFound(FileSorterError):
    """Raised when no workspace has been selected."""
    pass


class InvalidDirectory(FileSorterError):
    """Raised when a chosen path is not a directory or is inaccessible."""
    pass


class ConfigReadError(FileSorterError):
    """Raised when user_categories.json is malformed."""
    pass


class ConfigWriteError(FileSorterError):
    """Raised when we cannot write user_categories.json."""
    pass


class SortingError(FileSorterError):
    """Raised for generic file-operation failures during sorting."""
    pass


class DuplicateExtension(FileSorterError):
    """Raised when a user tries to add an extension that already exists."""
    pass


class EmptyExtension(FileSorterError):
    """Raised when a user supplies an empty extension."""
    pass


class EmptyCategoryName(FileSorterError):
    """Raised when a user tries to create a category with an empty name."""
    pass


class InvalidExtensionFormat(FileSorterError):
    """Raised when an extension contains illegal characters."""
    pass

