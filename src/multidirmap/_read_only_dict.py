"""Thin wrapper for dict or OrderedDict providing togglable read-only.

If the Python version keeps dict entries in insertion order, dict is used,
otherwise OrderedDict.
"""

import sys

if ((sys.version_info[:3] >= (3, 6, 0) and  # pragma: no cover
     sys.implementation.name == "cpython") or
        sys.version_info >= (3, 7, 0)):
    _dicttype = dict
else:  # pragma: no cover
    from collections import OrderedDict
    _dicttype = OrderedDict


def if_not_read_only(f):
    """Raise TypeError if decortd function is called while read only is True."""
    def wrapper(*args):
        if args[0]._read_only:
            raise TypeError("This dictionary is read only!")
        return f(*args)
    return wrapper


class ReadOnlyDict(_dicttype):
    """A dictionary that can be toggled read-only.

    Insertion order is maintained.
    Most magic methods are simply redirected to the parent, but defined here
    so they can be intercepted by @if_not_read_only.
    __eq__ is always redirected to dict so that comparison is order-independent.
    """

    _read_only = True

    def _set_read_only(self, read_only):
        """Toggle read only on or off."""
        self._read_only = read_only

    @if_not_read_only
    def __setitem__(self, key, value):
        """Redirects to __setitem__() of parent."""
        super(ReadOnlyDict, self).__setitem__(key, value)

    @if_not_read_only
    def __delitem__(self, key):
        """Redirects to __delitem__() of parent."""
        super(ReadOnlyDict, self).__delitem__(key)

    @if_not_read_only
    def clear(self):
        """Redirects to clear() of parent."""
        super(ReadOnlyDict, self).clear()  # pragma: no cover

    @if_not_read_only
    def pop(self, key, *args):
        """Redirects to pop() of parent."""
        return super(ReadOnlyDict, self).pop(key, *args)  # pragma: no cover

    @if_not_read_only
    def popitem(self):
        """Redirects to popitem() of parent."""
        return super(ReadOnlyDict, self).popitem()

    @if_not_read_only
    def setdefault(self, key, failobj=None):
        """Redirects to setdefault() of parent."""
        super(ReadOnlyDict, self).setdefault(key, failobj)  # pragma: no cover

    @if_not_read_only
    def update(self, *args, **kwargs):
        """Redirects to update() of parent."""
        super(ReadOnlyDict, self).update(*args, **kwargs)  # pragma: no cover

    def __eq__(self, other):
        """Redirects to __eq__() of dict.

        This redirection never points to OrderedDict to ensure comparisons are
        always order-insensitive, i.e. behaviour doesn't differ between Python
        versions.
        """
        return dict.__eq__(self, other)
