class OpenDotaAPIError(Exception):
    """Raised when OpenDota API data cannot be fetched."""


class DataLoadError(Exception):
    """Raised when locally saved data cannot be loaded."""
