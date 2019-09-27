Usage
=====

Creating / Updating a MultiDirMap
---------------------------------

.. code-block:: python

   >>> from multidirmap import MultiDirMap
   >>> crew = MultiDirMap(
           ["character", "portrayed_by", "role", "nicknames"],
           key_columns=2,
           data=[["Malcolm Reynolds", "Nathan Fillion", "Captain", ["Mal", "Captain Tight Pants"]],
                 ["Zoë Washburne", "Gina Torres", "First Mate"],
                 ["Hoban Washburne", "Alan Tudyk", "Pilot", "Wash"]])

MultiDirMap takes three arguments:

- "columns" is required and is a list of names for the columns in the map.
  The first column must be a key column and is below referred to as the
  "primary key column". All columns *must* be strings.
- "key_columns" gives the number of columns (in the order in which they are
  given in "columns" that should be key columns (and will only accept unique
  and hashable values). It is an optional argument and defaults to len(columns)
- "data" gives the data with which to initialize the MultiDirMap and is optional

Note that

.. code-block:: python

   >>> my_map = MultiDirMap(columns, data=my_data)

is exactly equivalent to

.. code-block:: python

   >>> my_map = MultiDirMap(columns)
   >>> my_map.update(my_data)

Data insertion order is maintained in the primary key column.

Accepted Data Formats
~~~~~~~~~~~~~~~~~~~~~

Data for the map can be provided in three different formats:

.. code-block:: python

   >>> crew.update([["Inara Serra", "Morena Baccarin", "Companion", "Ambassador"],
                    ["Jayne Cobb", "Adam Baldwin", "Mercenary", "Hero of Canton"]])
   >>> crew.update([{"character": "Kaywinnet Lee Frye", "portrayed_by": "Jewel Staite",
                     "role": "Mechanic", "nicknames": "Kaylee"},
                    {"character": "Simon Tam", "portrayed_by": "Sean Maher",
                     "role": "Medic"}])
   >>> crew.update({"River Tam": ["Summer Glau", None, "Méi-mei"],
                    "Derrial Book": ["Ron Glass", "Shepherd", "Preacher"]})

Values for non-key columns are optional.

All values in key columns must be hashable, so

.. code-block:: python

   >>> crew.update([[["Yolanda", "Saffron", "Bridget"], "Christina Hendricks", "Grifter"]])
   Traceback (most recent call last):
   ...
   TypeError: unhashable type: 'list'


Key Conflicts
~~~~~~~~~~~~~
In a normal Python dict, inserting an entry with a key that already exists
overwrites the existing entry. In a multidirectional mapping, things are a
little more complicated, so :code:`MultiDirMap.update()` takes two additional
keyword arguments, :code:`"overwrite"` and :code:`"skip_duplicates"`:

- "overwrite" (default: "primary" can take the values "none", "primary",
  "secondary", or "all" It indicates which key columns may be overwritten
  (with "secondary" meaning all key columns other than the primary one). An
  entry that has a value that is overwritten by an update will be completely
  removed from the MultiDirMap
- "skip_duplicates" (default False) describes the behaviour when an entry is
  encountered that may not be overwritten. If False, the update operation is
  aborted and a :code:`DuplicateKeyError` is raised. **An aborted update will
  never leave the map in a modified state, this includes the order of the
  primary key column.** So if the 10th entry in an update operation encounters a
  conflict, the first 9 will not end up in the map either. If True, conflicting
  entries will simply be skipped and all non-conflicting entries are inserted.

.. code-block:: python

   >>> crew.update([["Yolanda", "Christina Hendricks", "Grifter"]])
   >>> crew.update([["Bridget", "Christina Hendricks", "Grifter"]], overwrite="none")
   Traceback (most recent call last):
   ...
   DuplicateKeyError: One or more keys in ["Bridget", "Christina Hendricks", "Grifter"] were duplicates
   >>> crew.update([["Bridget", "Christina Hendricks", "Grifter"]], overwrite="primary")
   >>> crew["Bridget"].portrayed_by
   Christina Hendricks
   >>> crew["Yolanda"]
   Traceback (most recent call last):
   ...
   KeyError: "Yolanda"

Note that an entry that overwrites another one, can "free up" keys in other
columns for subsequent updates. This is not currently checked for within an
update operation, so it is possible that two consecutive updates with
:code:`overwrite="primary"` or :code:`overwrite="secondary` will succeed where
a combined operation would raise a DuplicateKeyError.

Key Column Methods
------------------

Under the hood, all key columns are stored as dicts and support dict methods
with one important caveat: **Key Columns in a MultiDirMap are read-only.** This
means that any of the following will raise a :code:`TypeError`:

.. code-block:: python

   >>> crew.portrayed_by["Nathan Fillion"] = [...]
   >>> del crew.portrayed_by["Nathan Fillion"]
   >>> crew.portrayed_by.clear()
   >>> crew.portrayed_by.pop("Nathan Fillion")
   >>> crew.portrayed_by.popitem()
   >>> crew.portrayed_by.setdefault("Nathan Fillion", default=None)
   >>> crew.portrayed_by.update(...)

On the other hand, all of the following methods will work as expected:

.. code-block:: python

   >>> crew.portrayed_by["Nathan Fillion"]
   >>> for name in crew.portrayed_by: ...
   >>> crew.portrayed_by.get("Nathan Fillion")
   >>> crew.portrayed_by.keys()
   >>> crew.portrayed_by.values()
   >>> crew.portrayed_by.items()

Operating directly on the MultiDirMap is equivalent to operate on its primary
key column, with the exception that writing access is permitted, so

.. code-block:: python

   >>> crew["Malcolm Reynolds"]
   >>> crew.character["Malcolm Reynolds"]

are equivalent, but in the case of

.. code-block:: python

   >>> del crew["Malcolm Reynolds"]
   >>> del crew.character["Malcolm Reynolds"]

the first one will work, while the second one will raise a :code:`TypeError`.

Note that for modifying methods other than :code:`update()`, behaviour will
always correspond to overwriting of primary key columns being permitted and
overwriting of secondary key columns being forbidden.

Row Elements
------------

Accessing an entry in a key column returns a custom object called a
:code:`MultiDirMapRow`. This object contains all data of the row (including
the key that was used to retrieve this element). So it is entirely possible
(though of questionable utility) to write

.. code-block:: python

   >>> crew["Malcolm Reynolds"].character
   Malcolm Reynolds

All attributes can be accessed with dot notation. Furthermore, a
:code:`MultiDirMapRow` has the methods :code:`to_list()` and :code:`to_dict()`:

.. code-block:: python

   >>> crew["Malcolm Reynolds"].to_list()
   ["Malcolm Reynolds", "Nathan Fillion", "Captain", ["Mal", "Captain Tight Pants"]]
   >>> crew["Malcolm Reynolds"].to_dict()
   {"character": "Malcolm Reynolds", "portrayed_by": "Nathan Fillion",
    "role": "Captain", "nicknames": ["Mal", "Captain Tight Pants"]}

Attributes can be modified and changes are propagated to the rest of the map
(subject to not conflicting with existing secondary keys):

.. code-block:: python

   >>> mal = crew["Malcolm Reynolds"]
   >>> mal.portrayed_by = "Alan Tudyk"
   Traceback (most recent call last):
   ...
   DuplicateKeyError: ...
   >>> mal.nicknames = None
   >>> crew.portrayed_by["Nathan Fillion"].to_list()
   ["Malcolm Reynolds", "Nathan Fillion", "Captain", None]

Equality Testing
----------------

Two MultiDirMaps will compare equal if their column names, number of key
columns, and entries are identical. Order - while preserved in the primary key
column regardless of Python version - does not affect equality testing.

Ordering
--------

Reordering the Secondary Key Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the primary key column always maintains insertion order, the order of the
secondary key columns can be scrambled by insertions that remove existing
elements by overwriting some of their keys. Consistent ordering between primary
and secondary key columns can be restored by calling :code:`reorder_secondary_keys()`
on a map. Note that this can be slow on large maps as it will recreate all
secondary dictionaries.

Sorting a MultiDirMap
~~~~~~~~~~~~~~~~~~~~~

An existing map can be sorted with an arbitrary comparison function:

.. code-block:: python

   >>> crew.sort(key=lambda entry: entry.portrayed_by, reverse=True)
   >>> print(crew)
   character*          portrayed_by*       role                nicknames
   ===============================================================================
   River Tam           Summer Glau         None                Méi-mei
   ...
   Hoban Washburne     Alan Tudyk          Pilot               Wash

- "key" is the function that serves as the key for the comparison
  function. If no key is given, sorting is done by the entries in the
  primary key column
- "reverse" (default :code:`False`) reverses the sorting.

Note that sorting can be slow on large maps as it will recreate all key dictionaries.

Printing
--------

Printing a MultiDirMap will output it as a table with key columns marked by an
asterisk. Formatting parameters can be set by

.. code-block:: python

   MultiDirMap.print_settings(max_width=80, max_cols=4, max_col_width=20)

- "max_width" sets the maximum total width of the table in characters
- "max_cols" set the maximum number of columns that will be displayed.
  Supernumerary columns will be replaced by "..."
- "max_col_width" sets the maximum width of each column in characters. Entries
  that are too long will be cropped.

.. code-block:: python

   >>> print(crew)
   character*          portrayed_by*       role                nicknames
   ===============================================================================
   Malcolm Reynolds    Nathan Fillion      Captain             ['Mal', 'Captain Ti
   Zoë Washburne       Gina Torres         First Mate          None
   Hoban Washburne     Alan Tudyk          Pilot               Wash
   Inara Serra         Morena Baccarin     Companion           Ambassador
   Jayne Cobb          Adam Baldwin        Mercenary           Hero of Canton
   Kaywinnet Lee Frye  Jewel Staite        Mechanic            Kaylee
   Simon Tam           Sean Maher          Medic               None
   River Tam           Summer Glau         None                Méi-mei
   Derrial Book        Ron Glass           Shepherd            Preacher
   >>> crew.print_settings(max_cols=3, max_col_width=15)
   >>> print(crew)
   character*      portrayed_by*   ... nicknames
   ===================================================
   Malcolm Reynold Nathan Fillion  ... ['Mal', 'Captai
   Zoë Washburne   Gina Torres     ... None
   Hoban Washburne Alan Tudyk      ... Wash
   Inara Serra     Morena Baccarin ... Ambassador
   Jayne Cobb      Adam Baldwin    ... Hero of Canton
   Kaywinnet Lee F Jewel Staite    ... Kaylee
   Simon Tam       Sean Maher      ... None
   River Tam       Summer Glau     ... Méi-mei
   Derrial Book    Ron Glass       ... Preacher
