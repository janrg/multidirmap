"""A multidirectional mapping with an arbitrary number of key columns."""
from contextlib import contextmanager

from ._multidirmaprow import generate_row_class
from ._read_only_dict import ReadOnlyDict
from ._util import DuplicateKeyError


class MultiDirMap(object):
    """A multidirectional mapping with an arbitrary number of key columns."""

    def __init__(self, columns, key_columns=None, data=None):
        """Create multidirectional mapping.

        columns is a list of column names.
        key_columns defines how many (in order) of columns should be key
        columns that the mapping can be indexed by.
        data initializes the mapping with the data provided (see also update()).
        """
        self._MultiDirMapRow = generate_row_class(columns)
        self._columns = columns
        self._key_columns = key_columns or len(columns)
        self._print_settings = {"max_width": 80, "max_cols": 4,
                                "max_col_width": 20}
        # For easier internal access than getattr
        self._key_dicts = {}
        for colname in columns[:key_columns]:
            setattr(self, colname, ReadOnlyDict())
            self._key_dicts[colname] = getattr(self, colname)
        # Primary key dict needs to be accessed frequently
        self._primary_key_dict = self._key_dicts[self._columns[0]]
        if data:
            self.update(data)

    def __getitem__(self, key):
        """Redirects to __getitem__ of the primary key dict."""
        return self._primary_key_dict[key]

    def __setitem__(self, key, value):
        """Redirects to __setitem__ of the primary key dicts."""
        self.update({key: value})

    def __delitem__(self, key):
        """Delete the indicated entry.

        Both the entry in the primary key dict and consequently orphaned
        entries in the secondary key dicts are deleted.
        """
        with self._writable():
            item = self._primary_key_dict.get(key)
            if not item:
                raise KeyError(key)
            for col, key in item.asdict().items():
                if col in self._key_dicts:
                    del self._key_dicts[col][key]

    def __len__(self):
        """Return number of entries in the mapping."""
        return len(self._primary_key_dict)

    def __eq__(self, other):
        """Test equality."""
        if self is other:
            return True
        if type(self) != type(other):
            return False
        return ((self._columns == other._columns) and
                (self._key_columns == other._key_columns) and
                (self._primary_key_dict == other._primary_key_dict))

    def __iter__(self):
        """Iterate over entries in the primary key dict."""
        return iter(self._primary_key_dict)

    def __str__(self):
        """Pretty print the map as a table.

        Column width and the number of columns (supernumerary ones are removed
        to the left of the last column and replaced by "...") are determined
        by the print settings.
        """
        n_output_cols = min(
            self._print_settings["max_cols"], len(self._columns))
        n_omitted_cols = max(
            len(self._columns) - self._print_settings["max_cols"], 0)
        col_width = min(
            self._print_settings["max_col_width"],
            (self._print_settings["max_width"] - 3 * n_omitted_cols -
             (n_output_cols + n_omitted_cols - 1)) // n_output_cols)
        total_width = (n_output_cols * col_width +
                       (n_output_cols + n_omitted_cols - 1) +
                       n_omitted_cols * 3)
        pad_format = "{:" + str(col_width) + "." + str(col_width) + "}"
        headers = ([pad_format.format(name[:col_width - 1] + "*")
                    for name in self._columns[:self._key_columns]] +
                   [pad_format.format(name[:col_width])
                    for name in self._columns[self._key_columns:]])
        if n_omitted_cols > 0:
            headers = headers[:n_output_cols - 1] + ["...", headers[-1]]

        output = [headers, [total_width * "="]]
        for row in self._primary_key_dict.values():
            entries = row.aslist()
            if len(headers) > n_output_cols:
                output.append(
                    [pad_format.format(str(value)[:col_width]) for value in
                     entries[:n_output_cols - 1]] + [
                        "...", pad_format.format(str(entries[-1])[:col_width])])
            else:
                output.append([pad_format.format(str(value)) for value in
                               entries])

        return "\n".join([" ".join(row) for row in output])

    def get(self, key, default=None):
        """Redirects to get() of the primary key dict."""
        return self._primary_key_dict.get(key, default)

    __marker = object()

    def pop(self, key, default=__marker):
        """Pop an entry from the mapping.

        Entry is returned from the primary key dict and it as well as all
        consequently orphaned entries are removed from the secondary key dicts.
        """
        item = self._primary_key_dict.get(key)
        if not item:
            if default is self.__marker:
                raise KeyError(key)
            return default
        self.__delitem__(key)
        return item

    def popitem(self):
        """Pop from the end of the primary key dict.

        All consequently orphaned entries are removed from the secondary
        key dicts.
        """
        if len(self._primary_key_dict) == 0:
            raise KeyError
        with self._writable():
            item = self._primary_key_dict.popitem()
            for col, key in item[1].asdict().items():
                if col in self._key_dicts and col != self._columns[0]:
                    del self._key_dicts[col][key]
        return item

    def keys(self):
        """Redirects to keys() of the primary key dict."""
        return self._primary_key_dict.keys()

    def values(self):
        """Redirects to values() of the primary key dict."""
        return self._primary_key_dict.values()

    def items(self):
        """Redirects to items() of the primary key dict."""
        return self._primary_key_dict.items()

    def clear(self):
        """Clear all key dicts, thereby deleting all stored data."""
        with self._writable():
            for key_dict in self._key_dicts.values():
                key_dict.clear()

    def update(self, data, overwrite="primary", skip_duplicates=False):
        """Update the map with the provided data.

        overwrite can be "none", "primary", "secondary", or "all" and determines
        whether an entry can still be added when it conflicts with an existing
        entry.
        skip_duplicates determines whether a conflicting entry that will not
        overwrite should be skipped. If False, an exception will be raised in
        that situation and a rollback performed, so that the update() operation
        does not change the state of the map.
        """
        data = self._format_data(data)
        added_entries = []
        backups = []
        to_delete = {col: set() for col in self._columns[:self._key_columns]}
        with self._writable():
            for row in data:
                self._add_entry(row, added_entries, backups, to_delete,
                                overwrite, skip_duplicates)
            for col, keys in to_delete.items():
                for key in keys:
                    del self._key_dicts[col][key]

    def print_settings(self, **kwargs):
        """Change the print settings for __str__().

        max_width gives the maximum width of the entire table.
        max_cols gives the maximum number of columns.
        max_col width gives the maximum width of each column.
        """
        for setting in ["max_width", "max_cols", "max_col_width"]:
            if setting in kwargs and type(kwargs[setting]) is int:
                self._print_settings[setting] = kwargs[setting]

    def _format_data(self, data):
        """Transform input data into a list of lists.

        If the input data is not in an accepted format, a ValueError is raised.
        """
        shaped_data = []
        if isinstance(data, list) or isinstance(data, tuple):
            for row in data:
                if isinstance(row, list) or isinstance(row, tuple):
                    if not self._key_columns <= len(row) <= len(self._columns):
                        raise ValueError(
                            "Encountered malformed data updating MultiDirMap:",
                            row)
                    shaped_data.append(
                        row + [None] * (len(self._columns) - len(row)))
                elif isinstance(row, dict):
                    if not set(self._columns[:self._key_columns]) <= set(row):
                        raise ValueError(
                            "Encountered malformed data updating MultiDirMap:",
                            row)
                    new_row = [row.get(col) for col in self._columns]
                    if None in new_row[:self._key_columns]:
                        raise ValueError(
                            "Encountered incomplete data updating MultiDirMap:",
                            row)
                    shaped_data.append(new_row)
                else:
                    raise ValueError(
                        "Encountered unexpected data format updating "
                        "MultiDirMap:", row)
        elif isinstance(data, dict):
            for primary_key, row in data.items():
                if isinstance(row, list) or isinstance(row, tuple):
                    if not (self._key_columns <= len(row) + 1 <=
                            len(self._columns)):
                        raise ValueError(
                            "Encountered malformed data updating MultiDirMap:",
                            row)
                    shaped_data.append(
                        [primary_key] + row +
                        [None] * (len(self._columns) - len(row) - 1))
                else:
                    raise ValueError(
                        "Encountered unexpected data format updating",
                        "MultiDirMap:", row)
        else:
            raise ValueError(
                "Encountered unexpected data format updating MultiDirMap.")
        return shaped_data

    def _add_entry(self, row, added_entries, backups, to_delete, overwrite,
                   skip_duplicates):
        """Add an entry to the map."""
        entries = dict(zip(self._columns, row))
        new_entry = self._MultiDirMapRow(self, entries)
        duplicates = {col: key in self._key_dicts[col] for col, key in
                      entries.items() if col in self._key_dicts}
        if not any(duplicates.values()):
            added_entry = {}
            for col, key in entries.items():
                if col in self._key_dicts:
                    self._key_dicts[col][key] = new_entry
                    added_entry[col] = key
            added_entries.append(added_entry)
            return
        # For any constellation that would not allow inserting the new entry we
        # either skip the entry or roll back and raise an error depending on
        # whether skip_duplicates is True
        if (overwrite == "none" or
            (overwrite == "primary" and any(
                [key for col, key
                 in duplicates.items() if col != self._columns[0]])) or
            (overwrite == "secondary" and
             duplicates[self._columns[0]])):
            if skip_duplicates:
                return
            else:
                self._rollback(added_entries, backups)
                raise DuplicateKeyError(
                    "One or more keys in {} were duplicates".format(
                        str(row)))
        self._determine_deletable(entries, duplicates, to_delete)
        if overwrite == "all":
            for col, key in entries.items():
                if col in self._key_dicts:
                    self._key_dicts[col][key] = new_entry
                    to_delete[col].discard(key)
            return

        # At this point, the only possibility is that there are duplicate keys
        # that we can overwrite but may need to roll back
        added_entry = {}
        backup = {}
        for col, key in entries.items():
            if col in self._key_dicts:
                if duplicates[col]:
                    backup[key] = [col, self._key_dicts[col][key]]
                else:
                    added_entry[col] = key
                self._key_dicts[col][key] = new_entry
                to_delete[col].discard(key)
        added_entries.append(added_entry)
        backups.append(backup)

    def _determine_deletable(self, entries, duplicates, to_delete):
        """Check which entries can be deleted at end of update() operation."""
        for col, key in entries.items():
            if col in self._key_dicts and duplicates[col]:
                for i, val in enumerate(
                        self._key_dicts[col][key].aslist()[:self._key_columns]):
                    to_delete[self._columns[i]].add(val)

    def _rollback(self, added_entries, backups):
        """Roll back to state before current update() operation started."""
        # First remove all the added entries so we don't get duplicate keys
        # when restoring from backups
        for added_entry in added_entries:
            for col, key in added_entry.items():
                del self._key_dicts[col][key]
        for backup in backups:
            for key, entry in backup.items():
                self._key_dicts[entry[0]][key] = entry[1]

    def _modify_row_attr(self, row, col, value, old_value):
        """Propagate modification of entry to all key dicts.

        Called on modification of a MultiDirMapRow element's attribute.
        Updates the appropriate key dicts to maintain consistentcy of the map.
        If there is a key conflict, a DuplicateKeyError exception is raised.
        """
        if value == row[col] or col not in self._key_dicts:
            return
        if value in self._key_dicts[col]:
            raise DuplicateKeyError(
                "Attempting to set a key to \"{}\", which already exists in "
                "column \"{}\"".format(value, col))
        with self._writable():
            self._key_dicts[col][value] = row
            del self._key_dicts[col][old_value]

    @contextmanager
    def _writable(self):
        """Make ReadOnlyDicts temporarily writable."""
        for keydict in self._key_dicts.values():
            keydict._set_read_only(False)
        try:
            yield
        finally:
            for keydict in self._key_dicts.values():
                keydict._set_read_only(True)
