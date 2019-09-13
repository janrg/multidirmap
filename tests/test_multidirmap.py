"""Test the functionality of a MultiDirMap."""

import pytest

from multidirmap import DuplicateKeyError
from multidirmap import MultiDirMap

pte_data = [
    ["symbol", "name", "atomic_number", "isotope_masses"],
    [
        ["H", "Hydrogen", 1, [1, 2, 3]],
        ["He", "Helium", 2, [4, 3]],
        ["Li", "Lithium", 3, [7, 6]],
        ["Be", "Beryllium", 4, [9, 10, 7]],
        ["B", "Boron", 5, [11, 10]],
        ["C", "Carbon", 6, [12, 13, 14, 11]],
        ["N", "Nitrogen", 7, [14, 15, 13]],
        ["O", "Oxygen", 8, [16, 18, 17]],
        ["F", "Fluorine", 9, [19, 18]],
        ["Ne", "Neon", 10, [20, 22, 21]],
    ],
]


def get_default_map(from_index=0, to_index=10, key_columns=3):
    """Generate a multidirmap for use in tests."""
    return MultiDirMap(
        pte_data[0], key_columns=key_columns, data=pte_data[1][from_index:to_index]
    )


class TestInputFormats:
    """Test that all allowed input formats are handled properly."""

    dol_data = {
        "H": ["Hydrogen", 1, [1, 2, 3]],
        "He": ["Helium", 2, [4, 3]],
        "Li": ["Lithium", 3, [7, 6]],
    }
    lod_data = [
        {
            "symbol": "H",
            "name": "Hydrogen",
            "atomic_number": 1,
            "isotope_masses": [1, 2, 3],
        },
        {
            "symbol": "He",
            "name": "Helium",
            "atomic_number": 2,
            "isotope_masses": [4, 3],
        },
        {
            "symbol": "Li",
            "name": "Lithium",
            "atomic_number": 3,
            "isotope_masses": [7, 6],
        },
    ]

    @pytest.mark.parametrize("data", [dol_data, lod_data], ids=["dol_data", "lod_data"])
    def test_input_formats(self, data):
        """Test the various possible input formats."""
        map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:3])
        map1 = MultiDirMap(pte_data[0], key_columns=3, data=data)
        assert map0 == map1


class TestPop:
    """Test the pop() method."""

    def test_pop_nonexistent(self):
        """Pop a nonexistent element."""
        map0 = get_default_map()
        with pytest.raises(KeyError):
            map0.pop("U")
        u = map0.pop("U", None)
        assert u is None

    def test_pop(self):
        """Pop an element."""
        map0 = get_default_map()
        h = map0.pop("H")
        assert h.aslist() == ["H", "Hydrogen", 1, [1, 2, 3]]
        assert map0 == get_default_map(from_index=1)

    def test_popitem(self):
        """Pop from end of map."""
        map0 = get_default_map()
        ne = map0.popitem()
        assert ne[0] == "Ne"
        assert ne[1].aslist() == ["Ne", "Neon", 10, [20, 22, 21]]
        assert map0 == get_default_map(to_index=9)

    def test_popitem_from_empty(self):
        """Pop from end of empty map."""
        map0 = get_default_map(from_index=0, to_index=0)
        with pytest.raises(KeyError):
            map0.popitem()


class TestPreventModifications:
    """Test that the read-only dicts prevent modification."""

    def test_prevent_assignment_to_keydict(self):
        """Assignment to key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol["He"] = "Hello world!"

    def test_prevent_del_from_keydict(self):
        """Deletion from key dict not possible."""
        with pytest.raises(TypeError):
            del get_default_map().symbol["He"]

    def test_prevent_clear_keydict(self):
        """Clearing key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol.clear()

    def test_prevent_pop_from_keydict(self):
        """Pop from key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol.pop("He")

    def test_prevent_popitem_from_keydict(self):
        """Popitem from key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol.popitem()

    def test_prevent_setdefault_to_keydict(self):
        """Setdefault on key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol.setdefault("He")

    def test_prevent_update_to_keydict(self):
        """Update to key dict not possible."""
        with pytest.raises(TypeError):
            get_default_map().symbol.update({"U": ["Uranium", 91, []]})


class TestReadAndWrite:
    """Test the methods that read to and write from a MultiDirMap."""

    def test_magic_get(self):
        """Retrieving an element via subscript."""
        map0 = get_default_map()
        be = ["Be", "Beryllium", 4, [9, 10, 7]]
        assert map0["Be"].aslist() == be
        assert map0.symbol["Be"].aslist() == be
        assert map0.name["Beryllium"].aslist() == be
        assert map0.atomic_number[4].aslist() == be

    def test_magic_set(self):
        """Setting an element via subscript."""
        map0 = get_default_map(to_index=9)
        map0["Ne"] = ["Neon", 10, [20, 22, 21]]
        assert map0 == get_default_map()

    def test_magic_set_duplicate_key_error(self):
        """Assigning which would cause DuplicateKeyError fails."""
        map0 = get_default_map()
        with pytest.raises(DuplicateKeyError):
            map0["X"] = ["Nothing", 3, []]

    def test_magic_del(self):
        """Delete entry from MultiDirMap."""
        map0 = get_default_map()
        del map0["He"]
        del map0["Be"]
        del map0["C"]
        del map0["O"]
        del map0["Ne"]
        with pytest.raises(KeyError):
            del map0["X"]
        assert map0 == MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][::2])

    def test_get_found(self):
        """Get method."""
        map0 = get_default_map()
        assert map0.get("C").aslist() == ["C", "Carbon", 6, [12, 13, 14, 11]]

    def test_get_not_found(self):
        """Get method for element not in map."""
        map0 = get_default_map()
        assert map0.get("X") is None

    def test_get_default(self):
        """Get method with default parameter for element not in map."""
        map0 = get_default_map()
        assert map0.get("X", "Dummy") == "Dummy"


class TestIter:
    """Test iteration over a MultiDirMap."""

    def test_iter(self):
        """Iteration over a MultiDirmap."""
        assert [key for key in get_default_map()] == [
            "H",
            "He",
            "Li",
            "Be",
            "B",
            "C",
            "N",
            "O",
            "F",
            "Ne",
        ]

    def test_keys(self):
        """Iteration over the keys."""
        map0 = get_default_map()
        for i, key in enumerate(map0.keys()):
            assert map0[key].aslist() == pte_data[1][i]

    def test_values(self):
        """Iteration over the values."""
        map0 = get_default_map()
        for i, value in enumerate(map0.values()):
            assert value.aslist() == pte_data[1][i]

    def test_items(self):
        """Iteration over the items."""
        map0 = get_default_map()
        for key, value in map0.items():
            assert map0[key] == value


class TestLen:
    """Test len(MultiDirMap)."""

    @pytest.mark.parametrize("to_index, length", [(0, 0), (10, 10)])
    def test_len(self, to_index, length):
        """Length of a MultiDirMap."""
        map0 = get_default_map(to_index=to_index)
        assert len(map0) == length


class TestStr:
    """Test string output."""

    default_str = (
        "symbol*             name*               atomic_number*      isotope_masses     \n"  # noqa: E501
        "===============================================================================\n"  # noqa: E501
        "H                   Hydrogen            1                   [1, 2, 3]          \n"  # noqa: E501
        "He                  Helium              2                   [4, 3]             \n"  # noqa: E501
        "Li                  Lithium             3                   [7, 6]             \n"  # noqa: E501
        "Be                  Beryllium           4                   [9, 10, 7]         \n"  # noqa: E501
        "B                   Boron               5                   [11, 10]           \n"  # noqa: E501
        "C                   Carbon              6                   [12, 13, 14, 11]   "  # noqa: E501
    )
    compact_str = (
        "symbol*   name*     ... isotope_m\n"
        "=================================\n"
        "H         Hydrogen  ... [1, 2, 3]\n"
        "He        Helium    ... [4, 3]   \n"
        "Li        Lithium   ... [7, 6]   \n"
        "Be        Beryllium ... [9, 10, 7\n"
        "B         Boron     ... [11, 10] \n"
        "C         Carbon    ... [12, 13, "
    )

    @pytest.mark.parametrize(
        "print_settings, output",
        [({}, default_str), ({"max_cols": 3, "max_col_width": 9}, compact_str)],
        ids=["default settings", "compact"],
    )
    def test_str(self, print_settings, output):
        """Output MultiDirMap as string."""
        map0 = get_default_map(to_index=6)
        map0.print_settings(**print_settings)
        assert str(map0) == output


class TestUpdate:
    """Test the update method of a MultiDirMap."""

    def test_duplicate_key_update_raises_exception_and_doesnt_modify_map(self):
        """A duplicate key during update raises exception and doesn't modify map."""
        map0 = get_default_map(to_index=3)
        with pytest.raises(DuplicateKeyError):
            map0.update(pte_data[1][3:] + pte_data[1][0:1])
        assert map0 == get_default_map(to_index=3)

    def test_update_leaves_key_columns_consistent(self):
        """An update leaves the key columns consistent."""
        map0 = get_default_map(to_index=3)
        map0.update([["He", "NotHelium", 20]])
        assert map0["He"].aslist() == ["He", "NotHelium", 20, None]
        assert map0["He"] is map0.name["NotHelium"]
        assert map0["He"] is map0.atomic_number[20]
        assert is_consistent(map0)

    def test_error_during_update_rolls_back_changes(self):
        """If an error occurs during update, all changes are rolled back."""
        map0 = get_default_map()
        with pytest.raises(DuplicateKeyError):
            map0.update(
                [["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 9, []]],
                overwrite="secondary",
            )
        assert is_consistent(map0)
        assert map0 == get_default_map()
        assert list(map0.symbol.keys()) == [
            "H",
            "He",
            "Li",
            "Be",
            "B",
            "C",
            "N",
            "O",
            "F",
            "Ne",
        ]

    def test_overwriting_secondary_key_removes_obsolete_primary_key(self):
        """If secondary keys are overwritten, obsolete primary keys are removed."""
        map0 = get_default_map()
        map0.update([["X", "Helium", 3, []], ["Y", "Y", 9, []]], overwrite="secondary")
        assert is_consistent(map0)
        with pytest.raises(KeyError):
            map0["He"]
        assert map0.name["Helium"].aslist() == ["X", "Helium", 3, []]
        assert list(map0.keys()) == ["H", "Be", "B", "C", "N", "O", "Ne", "X", "Y"]

    def test_update_with_overwrite_all_overwrites_all_entries_with_key_conflicts(self):
        """Setting overwrite to "all" overwrites all entries with key conflicts."""
        map0 = get_default_map()
        map0.update(
            [["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 9, []]],
            overwrite="all",
        )
        assert is_consistent(map0)
        assert map0["H"].aslist() == ["H", "H", 9, []]
        assert map0.name["Helium"].aslist() == ["X", "Helium", 3, []]
        assert list(map0.keys()) == ["H", "Be", "B", "C", "N", "O", "Ne", "X"]

    def test_skip_duplicates_silently_ignores_duplicates_that_are_not_overwritten(self):
        """Setting skip_duplicates to True will ignore duplicates not overwritten."""
        map0 = get_default_map()
        map0.update(
            [["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 10, []]],
            overwrite="secondary",
            skip_duplicates=True,
        )
        assert is_consistent(map0)
        with pytest.raises(KeyError):
            map0["He"]
        assert map0["H"].aslist() == ["H", "Hydrogen", 1, [1, 2, 3]]
        assert map0.atomic_number[10].aslist() == ["Ne", "Neon", 10, [20, 22, 21]]

    @pytest.mark.parametrize(
        "update_data",
        [
            [["U"]],
            [
                {
                    "symbol": "U",
                    "name": "Uranium",
                    "isotope_masses": [238, 235, 234, 236, 233, 232],
                }
            ],
            [
                {
                    "symbol": "U",
                    "name": "Uranium",
                    "atomic_number": None,
                    "isotope_masses": [238, 235, 234, 236, 233, 232],
                }
            ],
            ["Uranium"],
            {"U": ("Uranium", 92, [], "Supernumary value")},
            {"U": "Uranium"},
            "Uranium",
        ],
        ids=[
            "missing secondary keys from list",
            "missing secondary keys from dict",
            "None value in secondary keys",
            "non-collection in outer list",
            "unrecognized key",
            "non-collection in dict value",
            "non-collection",
        ],
    )
    def test_bad_data_format(self, update_data):
        """An update with invalid data raises a ValueError."""
        map0 = get_default_map(to_index=3)
        with pytest.raises(ValueError):
            map0.update(update_data)


class TestEquality:
    """Test the equality operators."""

    @pytest.mark.parametrize(
        "map0, map1, equals",
        [
            (get_default_map(), get_default_map(), True),
            (
                get_default_map(),
                MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][::-1]),
                True,
            ),
            (get_default_map(), get_default_map(key_columns=2), False),
            (
                get_default_map(from_index=0, to_index=0),
                get_default_map(from_index=0, to_index=0, key_columns=2),
                False,
            ),
            (
                get_default_map(from_index=0, to_index=0),
                MultiDirMap(["symbol", "name", "atomic_number"], key_columns=3),
                False,
            ),
            (get_default_map(), "Hello World", False),
        ],
        ids=[
            "same order",
            "different order",
            "different key columns",
            "different key columns no data",
            "different columns no data",
            "different types",
        ],
    )
    def test_equal(self, map0, map1, equals):
        """Behaviour of == and != operators."""
        assert (map0 == map1) is equals
        assert (map0 != map1) is (not equals)


class TestModifyRow:
    """Test modifying rows."""

    def test_modify_key_column_value(self):
        """Modify the value of a key column."""
        map0 = get_default_map()
        map0["Li"].atomic_number = 20
        assert 3 not in map0.atomic_number
        assert map0.atomic_number[20].aslist() == ["Li", "Lithium", 20, [7, 6]]
        assert is_consistent(map0)

    def test_raise_duplicate_key_error(self):
        """Modify the value of a key column causing a KeyError."""
        map0 = get_default_map()
        with pytest.raises(DuplicateKeyError):
            map0["B"].name = "Carbon"
        assert is_consistent(map0)


class TestClear:
    """Test clearing a MultiDirMap."""

    def test_clear(self):
        """Test the clear() method."""
        map0 = get_default_map()
        map1 = get_default_map(from_index=0, to_index=0)
        map0.clear()
        assert len(map0) == 0
        assert map0 == map1


class TestReorderSecondaryKeys:
    """Test reordering secondary keys."""

    def test_reorder_secondary_keys(self):
        """Test the reorder_secondary_keys() method.

        It should ensure that the order of entries in the secondary key columns
        corresponds to the order of entries in the primary key column.
        """
        map0 = get_default_map()
        map1 = get_default_map()
        map0.update([["O", "NotOxygen", 999, [9999]]])
        map0.update([["O", "Oxygen", 8, [16, 18, 17]]])
        map0.reorder_secondary_keys()
        assert is_consistent(map0)
        assert map0 == map1
        for column in map0._columns[: map0._key_columns]:
            assert list(getattr(map0, column).keys()) == list(
                getattr(map1, column).keys()
            )


class TestSort:
    """Test sorting a MultiDirMap."""

    def test_default_sort(self):
        """Default sorting (by primary key column)."""
        map0 = get_default_map()
        map0.sort()
        assert map0 == get_default_map()
        assert list(map0.keys()) == sorted(map0.keys())

    def test_custom_sort(self):
        """Sorting with custom comparator."""
        map0 = get_default_map()
        map0.sort(key=lambda entry: entry.atomic_number, reverse=True)
        assert map0 == get_default_map()
        assert list(map0.atomic_number.keys()) == list(range(10, 0, -1))


def is_consistent(mdmap):
    """Check whether a MultiDirMap is internally consistent.

    Specifically this tests that all key dicts have the same length and that
    each row is referred to by the appropriate key in each key dicts.
    """
    cols = mdmap._columns
    for col in cols[1 : mdmap._key_columns]:
        if len(getattr(mdmap, col)) != len(mdmap):  # pragma: no cover
            return False
    for key, entry in mdmap.items():
        for col in cols[1 : mdmap._key_columns]:
            if getattr(mdmap, col)[getattr(entry, col)] != entry:  # pragma: no cover
                return False
    return True
