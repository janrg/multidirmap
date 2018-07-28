"""MultiDirMapRow is an object that holds a row of entries in a MultiDirMap.

The object uses slots to prevent arbitrary attributes being added (and to save
space for Python versions that do not yet implement key-sharing dicts). Since
the slots required depend on the parent MultiDirMap, the class is dynamically
generated via generate_row_class().
"""


def generate_row_class(slots):
    """Dynamically create a MultiDirMapRow class with given slots."""
    class MultiDirMapRow(object):
        """An entry in a MultiDirMap.

        Attributes are given as slots. _parent holds a reference to the
        MultiDirMap instance for which this class was created so that a
        change to a MultiDirMapRow instance can trigger an update of the
        parent.
        """

        __slots__ = ["_parent"] + slots

        def __init__(self, parent, values):
            # Need to avoid own __setattr__ for this one assignment
            super(MultiDirMapRow, self).__setattr__("_parent", parent)
            for key, value in values.items():
                super(MultiDirMapRow, self).__setattr__(key, value)

        def aslist(self):
            """Return contents as list in correct order."""
            return [getattr(self, key) for key in self.__slots__[1:]]

        def asdict(self):
            """Return contents as dict."""
            return {key: getattr(self, key) for key in self.__slots__[1:]}

        def __setattr__(self, attr, value):
            self._parent._modify_row_attr(
                self, attr, value, getattr(self, attr))
            super(MultiDirMapRow, self).__setattr__(attr, value)

        def __getitem__(self, key):
            return getattr(self, key)

        def __setitem__(self, key, value):
            setattr(self, key, value)

        def __eq__(self, other):
            if self is other:
                return True
            return self.aslist() == other.aslist()

    return MultiDirMapRow
