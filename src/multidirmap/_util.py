"""Other definitions needed by MultiDirMap."""
from enum import Enum


class DuplicateKeyError(Exception):
    """Raised when secondary key is not unique."""


class Overwrite(str, Enum):
    """Enum for setting the overwrite mode."""

    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ALL = "all"
