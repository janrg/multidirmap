
Changelog
=========

0.3.0 (2019-10-03)
------------------

* :code:`overwrite` now takes an enum :code:`Overwrite` (backported to 2.7 via
  :code:`enum34`) with values :code:`NONE`, :code:`PRIMARY`, :code:`SECONDARY`,
  or :code:`ALL` instead of string values (though the implementation is backwards
  compatible to using the old string values).
* :code:`copy.copy()` and :code:`copy.deepcopy()` now work properly on a MultiDirMap
* :code:`aslist()` and :code:`asdict()` on row elements renamed to :code:`to_list()`
  and :code:`to_dict()`
* new method :code:`to_list()` which returns complete map data as a list of lists

0.2.0 (2019-07-12)
------------------

* Custom sorting
* Reordering of secondary keys

0.1.0 (2018-07-28)
------------------

* First release on PyPI.
