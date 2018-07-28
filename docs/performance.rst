Performance
===========

Information below is provided only to give an idea of what kind of performance
can be expected from a MultiDirMap. It is not meant as a replacement for any
of the data structures mentioned below, but its flexibility affords it some
overlap with them.

Compared to dict
----------------

A MultiDirMap with two columns, one of which is a key column, exhibits slightly
slower retrieval than Python's built-in dict with significantly slower creation.
**Do not use a MultiDirMap when a dict would suffice** :-)

Compared to bidict
------------------
A MultiDirMap with two columns that are both key columns is *slightly* slower in
both retrieval and creation than a `bidict <https://github.com/jab/bidict>`__.

Compared to pandas DataFrame
----------------------------
A pandas DataFrame (which does not ensure uniqueness of keys) has significantly
faster creation than a MultiDirMap (since it is an array under the hood) but in
retrieval, a MultiDirMap vastly outperforms it, since the DataFrame retrieves on
O(n) as opposed to O(1).
