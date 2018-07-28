multidirmap
===========

Multidirectional map where an arbitrary number of columns can be used as keys.

Status
------

.. image:: https://readthedocs.org/projects/multidirmap/badge/?style=flat
   :target: https://readthedocs.org/projects/multidirmap
   :alt: Documentation Status

.. image:: https://travis-ci.org/janrg/multidirmap.svg?branch=master
   :alt: Travis-CI Build Status
   :target: https://travis-ci.org/janrg/multidirmap

.. image:: https://ci.appveyor.com/api/projects/status/github/janrg/multidirmap?branch=master&svg=true
   :alt: AppVeyor Build Status
   :target: https://ci.appveyor.com/project/janrg/multidirmap

.. image:: https://codecov.io/github/janrg/multidirmap/coverage.svg?branch=master
   :alt: Coverage Status
   :target: https://codecov.io/github/janrg/multidirmap

.. image:: https://img.shields.io/pypi/v/multidirmap.svg
   :alt: PyPI Package latest release
   :target: https://pypi.python.org/pypi/multidirmap

.. image:: https://img.shields.io/pypi/wheel/multidirmap.svg
   :alt: PyPI Wheel
   :target: https://pypi.python.org/pypi/multidirmap

.. image:: https://img.shields.io/pypi/pyversions/multidirmap.svg
   :alt: Supported versions
   :target: https://pypi.python.org/pypi/multidirmap

.. image:: https://img.shields.io/pypi/implementation/multidirmap.svg
   :alt: Supported implementations
   :target: https://pypi.python.org/pypi/multidirmap

.. image:: https://img.shields.io/pypi/l/multidirmap.svg
   :target: https://raw.githubusercontent.com/janrg/multidirmap/master/LICENSE
   :alt: License

Installation
------------

.. code-block:: bash

   $ pip install multidirmap

Documentation
-------------

https://multidirmap.readthedocs.io/

Quick Start
-----------

.. code-block:: python

   >>> from multidirmap import MultiDirMap
   >>> crew = MultiDirMap(
           ["character", "portrayed_by", "role", "nicknames"],
           key_columns=2,
           data=[["Malcolm Reynolds", "Nathan Fillion", "Captain", ["Mal", "Captain Tight Pants"]],
                 ["Zoë Washburne", "Gina Torres", "First Mate"],
                 ["Hoban Washburne", "Alan Tudyk", "Pilot", "Wash"]])
   >>> crew["Malcolm Reynolds"].role
   Captain
   >>> crew.portrayed_by["Nathan Fillion"].nicknames
   ["Mal", "Captain Tight Pants"]

Features
--------

- As many columns as desired can be used as key columns for the mapping
- O(1) retrieval from any key column
- Internal consistency is maintained through any modifications to the contents
- Insertion order is maintained in the primary key column
- Built-in pretty printing of the mapping

Use Cases
---------

Dictionaries are ubiquitous in Pyton and provide an extremely useful and fast
mapping from keys to values. Sometimes, a single, uni-directional mapping is not
enough, though, and while `bidict <https://github.com/jab/bidict>`__ extends
this functionality to a bidirectional mapping, *multidirmap* provides an
array-like datastructure where any number of columns can be used for O(1)
retrieval. In its simplest implementation (2 columns, one of which is a key
column), it essentially provides the same functionality as a dict, albeit with
additional overhead (don't do that...). 2 columns that are both key columns
will behave somewhat like a bidict, albeit with slightly different syntax. But
*multidirmap* is significantly more flexible in that any number of key and
non-key columns can be used.
A somewhat similar effect could be achieved with pandas DataFrames, though these
(1) will not ensure uniqueness of keys, hence a retrieval may return any number
of rows, (2) use an array structure, hence retrieval is O(n) which for large
arrays can get *very* slow, and (3) require the installation of pandas, which
is a rather large library to include just for this feature.

Say we want to work with information from the Periodic Table of Elements, like

.. code-block:: python

   [["H", "Hydrogen", 1, [1, 2, 3]],
    ["He", "Helium", 2, [4, 3]],
    ["Li", "Lithium", 3, [7, 6]],
    ...
    ["Og", "Oganesson", 118, [295, 294]]]

where the columns indicate symbol, name, atomic number, and nucleon numbers of
isotopes respectively. The first three columns are obvious candidates for key
columns as they are by definition unique. *multidirmap* allows placing this
information in a unified datastructure where questions like "What are the
isotope nucleon numbers of Lithium?", "What is the chemical element symbol of
Potassium?", or "What is the name of the element with atomic number 46?" can
be asked with a simple syntax and O(1) retrieval. Any number of additional
key and non-key columns could be added.

The use case that prompted the development on this package involved the *struct*
module: For a binary interface I needed to convert back and forth between (1)
a string representation of the variable type, (2) an integer representation
of the variable type, (3) the struct format char, and (4) the size in bytes of
the variable. Again, 1-3 are obvious candidates for key columns, with 4 being
a non-key column. Without *multidirmap*, several separate dicts have to be used
to provide each needed mapping from one column to another and there is easy way
to ensure that these dicts remain consistent with each other through possible
changes. 
