"""Test the functionality of a MultiDirMap."""

import pytest

from multidirmap import DuplicateKeyError
from multidirmap import MultiDirMap


@pytest.fixture(scope="module")
def pte_data():
    """Return common data for test cases.

    Extract from the Periodic Table of Elements.
    """
    return [["symbol", "name", "atomic_number", "isotope_masses"],
            [["H", "Hydrogen", 1, [1, 2, 3]],
             ["He", "Helium", 2, [4, 3]],
             ["Li", "Lithium", 3, [7, 6]],
             ["Be", "Beryllium", 4, [9, 10, 7]],
             ["B", "Boron", 5, [11, 10]],
             ["C", "Carbon", 6, [12, 13, 14, 11]],
             ["N", "Nitrogen", 7, [14, 15, 13]],
             ["O", "Oxygen", 8, [16, 18, 17]],
             ["F", "Fluorine", 9, [19, 18]],
             ["Ne", "Neon", 10, [20, 22, 21]]]]


def test_input_formats(pte_data):
    """Test the various possible input formats."""
    data1 = {"H": ["Hydrogen", 1, [1, 2, 3]],
             "He": ["Helium", 2, [4, 3]],
             "Li": ["Lithium", 3, [7, 6]]}
    data2 = [{"symbol": "H", "name": "Hydrogen", "atomic_number": 1,
              "isotope_masses": [1, 2, 3]},
             {"symbol": "He", "name": "Helium", "atomic_number": 2,
              "isotope_masses": [4, 3]},
             {"symbol": "Li", "name": "Lithium", "atomic_number": 3,
              "isotope_masses": [7, 6]}]
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:3])
    map1 = MultiDirMap(pte_data[0], key_columns=3, data=data1)
    map2 = MultiDirMap(pte_data[0], key_columns=3, data=data2)
    assert map0 == map1
    assert map1 == map2


def test_pop(pte_data):
    """Test popping from a MultiDirMap."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map1 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][1:])
    map2 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][1:-1])
    map3 = MultiDirMap(pte_data[0], key_columns=3)
    with pytest.raises(KeyError):
        map0.pop("U")
    u = map0.pop("U", None)
    assert u is None
    h = map0.pop("H")
    assert h.aslist() == ["H", "Hydrogen", 1, [1, 2, 3]]
    assert map0 == map1
    ne = map0.popitem()[1]
    assert ne.aslist() == ["Ne", "Neon", 10, [20, 22, 21]]
    assert map0 == map2
    with pytest.raises(KeyError):
        map3.popitem()


def test_read_only_dict(pte_data):
    """Test that the ReadOnlyDict successfully suppresses modifications."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    with pytest.raises(TypeError):
        map0.symbol["He"] = "Hello world!"
    with pytest.raises(TypeError):
        del map0.symbol["He"]
    with pytest.raises(TypeError):
        map0.symbol.clear()
    with pytest.raises(TypeError):
        map0.symbol.pop("He")
    with pytest.raises(TypeError):
        map0.symbol.popitem()
    with pytest.raises(TypeError):
        map0.symbol.setdefault("He")
    with pytest.raises(TypeError):
        map0.symbol.update({"U": ["Uranium", 91, []]})


def test_magic_get_set_del(pte_data):
    """Test the __get__(), __set__(), and __del__() magic methods."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:9])
    map1 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map2 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][::2])
    be = ["Be", "Beryllium", 4, [9, 10, 7]]
    assert map0["Be"].aslist() == be
    assert map0.symbol["Be"].aslist() == be
    assert map0.name["Beryllium"].aslist() == be
    assert map0.atomic_number[4].aslist() == be
    map0["Ne"] = ["Neon", 10, [20, 22, 21]]
    assert map0 == map1
    del map0["He"]
    del map0["Be"]
    del map0["C"]
    del map0["O"]
    del map0["Ne"]
    with pytest.raises(KeyError):
        del map0["X"]
    assert map0 == map2
    with pytest.raises(DuplicateKeyError):
        map0["X"] = ["Nothing", 3, []]


def test_get(pte_data):
    """Test the get() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    c = map0.get("C")
    x = map0.get("X")
    y = map0.get("Y", "Dummy")
    assert c.aslist() == ["C", "Carbon", 6, [12, 13, 14, 11]]
    assert x is None
    assert y == "Dummy"


def test_iter_keys_values_items(pte_data):
    """Test the iter-related methods __iter__(), keys(), values(), items()."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    keys = [key for key in map0]
    assert keys == ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
    assert keys == list(map0.keys())
    for i, value in enumerate(map0.values()):
        assert value.aslist() == pte_data[1][i]
    for key, value in map0.items():
        assert(map0[key] == value)


def test_len(pte_data):
    """Test the __len__() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3)
    assert len(map0) == 0
    map0.update(pte_data[1])
    assert len(map0) == 10


def test_str(pte_data):
    """Test the __str__() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:6])
    string0 = ("symbol*             name*               atomic_number*      isotope_masses     \n"  # noqa: E501
               "===============================================================================\n"  # noqa: E501
               "H                   Hydrogen            1                   [1, 2, 3]          \n"  # noqa: E501
               "He                  Helium              2                   [4, 3]             \n"  # noqa: E501
               "Li                  Lithium             3                   [7, 6]             \n"  # noqa: E501
               "Be                  Beryllium           4                   [9, 10, 7]         \n"  # noqa: E501
               "B                   Boron               5                   [11, 10]           \n"  # noqa: E501
               "C                   Carbon              6                   [12, 13, 14, 11]   ")   # noqa: E501
    assert str(map0) == string0
    map0.print_settings(max_cols=3, max_col_width=9)
    string1 = ("symbol*   name*     ... isotope_m\n"
               "=================================\n"
               "H         Hydrogen  ... [1, 2, 3]\n"
               "He        Helium    ... [4, 3]   \n"
               "Li        Lithium   ... [7, 6]   \n"
               "Be        Beryllium ... [9, 10, 7\n"
               "B         Boron     ... [11, 10] \n"
               "C         Carbon    ... [12, 13, ")
    assert str(map0) == string1


def test_update(pte_data):
    """Test the update() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:3])
    map1 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1][:3])
    with pytest.raises(DuplicateKeyError):
        map1.update(pte_data[1][3:] + pte_data[1][0:1])
    assert map0 == map1
    map1.update([["He", "NotHelium", 20]])
    assert map1["He"].aslist() == ["He", "NotHelium", 20, None]
    assert map1["He"] is map1.name["NotHelium"]
    assert map1["He"] is map1.atomic_number[20]
    assert is_consistent(map1)
    map2 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map3 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    with pytest.raises(DuplicateKeyError):
        map3.update(
            [["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 9, []]],
            overwrite="secondary")
    assert is_consistent(map3)
    assert map2 == map3
    assert (list(map3.symbol.keys()) ==
            ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"])
    map4 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map4.update([["X", "Helium", 3, []], ["Y", "Y", 9, []]],
                overwrite="secondary")
    assert is_consistent(map4)
    with pytest.raises(KeyError):
        map4["He"]
    assert map4.name["Helium"].aslist() == ["X", "Helium", 3, []]
    assert list(map4.keys()) == ["H", "Be", "B", "C", "N", "O", "Ne", "X", "Y"]
    map5 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map5.update([["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 9, []]],
                overwrite="all")
    assert is_consistent(map5)
    assert map5["H"].aslist() == ["H", "H", 9, []]
    assert map5.name["Helium"].aslist() == ["X", "Helium", 3, []]
    assert list(map5.keys()) == ["H", "Be", "B", "C", "N", "O", "Ne", "X"]
    map6 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map6.update(
        [["X", "Helium", 3, []], ["Y", "Y", 9, []], ["H", "H", 10, []]],
        overwrite="secondary", skip_duplicates=True)
    assert is_consistent(map6)
    with pytest.raises(KeyError):
        map6["He"]
    assert map6["H"].aslist() == ["H", "Hydrogen", 1, [1, 2, 3]]
    assert map6.atomic_number[10].aslist() == ["Ne", "Neon", 10, [20, 22, 21]]
    with pytest.raises(ValueError):
        map0.update([["U"]])
    with pytest.raises(ValueError):
        map0.update([{"symbol": "U", "name": "Uranium",
                      "isotope_masses": [238, 235, 234, 236, 233, 232]}])
    with pytest.raises(ValueError):
        map0.update([{"symbol": "U", "name": "Uranium", "atomic_number": None,
                      "isotope_masses": [238, 235, 234, 236, 233, 232]}])
    with pytest.raises(ValueError):
        map0.update(["Uranium"])
    with pytest.raises(ValueError):
        map0.update({"U": ("Uranium", 92, [], "Supernumary value")})
    with pytest.raises(ValueError):
        map0.update({"U": "Uranium"})
    with pytest.raises(ValueError):
        map0.update("Uranium")


def test_equality(pte_data):
    """Test the __eq__() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map1 = MultiDirMap(pte_data[0], key_columns=2, data=pte_data[1])
    map2 = MultiDirMap(pte_data[0], key_columns=3)
    map3 = MultiDirMap(pte_data[0][:3], key_columns=3)
    assert map0 == map0
    assert map0 != map1
    assert map0 != map2
    assert map0 != "Hello World"
    assert map2 != map3


def test_modify_row(pte_data):
    """Test that modifying a MultiDirMapRow element works as expected."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map0["H"].atomic_number = 1
    map0["Li"].atomic_number = 20
    assert is_consistent(map0)
    map0["Ne"]["name"] = "NotNeon"
    assert is_consistent(map0)
    with pytest.raises(DuplicateKeyError):
        map0["B"].name = "Carbon"
    assert is_consistent(map0)


def test_clear(pte_data):
    """Test the clear() method."""
    map0 = MultiDirMap(pte_data[0], key_columns=3, data=pte_data[1])
    map1 = MultiDirMap(pte_data[0], key_columns=3)
    map0.clear()
    assert len(map0) == 0
    assert map0 == map1


def is_consistent(mdmap):
    """Check whether a MultiDirMap is internally consistent.

    Specifically this tests that all key dicts have the same length and that
    each row is referred to by the appropriate key in each key dicts.
    """
    cols = mdmap._columns
    for col in cols[1:mdmap._key_columns]:
        if len(getattr(mdmap, col)) != len(mdmap):  # pragma: no cover
            return False
    for key, entry in mdmap.items():
        for col in cols[1:mdmap._key_columns]:
            if getattr(mdmap,
                       col)[getattr(entry, col)] != entry:  # pragma: no cover
                return False
    return True
