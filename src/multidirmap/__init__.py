"""A multidirectional mapping with an arbitrary number of key columns."""

from .multidirmap import DuplicateKeyError
from .multidirmap import MultiDirMap

__version__ = "0.2.0"
__all__ = ["MultiDirMap", "DuplicateKeyError"]
