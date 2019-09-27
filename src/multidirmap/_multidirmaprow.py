"""MultiDirMapRow is an object that holds a row of entries in a MultiDirMap.

The object uses slots to prevent arbitrary attributes being added (and to save
space for Python versions that do not yet implement key-sharing dicts). Since
the slots required depend on the parent MultiDirMap, the class is dynamically
generated via generate_row_class().
"""


class MultiDirMapRowBase(object):
    """An entry in a MultiDirMap.

    Attributes are given as slots. _parent holds a reference to the
    MultiDirMap instance for which this class was created so that a
    change to a MultiDirMapRow instance can trigger an update of the
    parent.
    """

    __slots__ = ["_parent"]

    def __init__(self, parent, values):
        """Create a row in a MultiDirMap.

        parent is a link back to the map to which this row belongs
        values is a dict with the values for this row
        """
        # Need to avoid own __setattr__ for this one assignment
        super(MultiDirMapRowBase, self).__setattr__("_parent", parent)
        for key, value in values.items():
            super(MultiDirMapRowBase, self).__setattr__(key, value)

    def to_list(self):
        """Return contents as list in correct order."""
        return [getattr(self, key) for key in self.__slots__]

    def to_dict(self):
        """Return contents as dict."""
        return {key: getattr(self, key) for key in self.__slots__}

    def __setattr__(self, attr, value):
        """Set value in this row and update the parent map accordingly."""
        self._parent._modify_row_attr(self, attr, value, getattr(self, attr))
        super(MultiDirMapRowBase, self).__setattr__(attr, value)

    def __getitem__(self, key):
        """Get value in this row."""
        return getattr(self, key)

    def __setitem__(self, key, value):
        """Set value in this row and update the parent map accordingly."""
        setattr(self, key, value)

    def __eq__(self, other):
        """Test equality."""
        if self is other:
            return True
        return self.to_list() == other.to_list()

    def __ne__(self, other):
        """Test inequality (required for Python 2)."""
        return not self == other
