import pytest
from names import Names


def test_names_lookup():
    '''Check Lookup function performs correctly.'''
    names = Names()
    assert names.lookup(['craft', 'arctic']) == [0, 1]
    assert names.lookup(['arctic', 'town', 'craft']) == [1, 2, 0]
    assert names.lookup(['craft']) == [0]
    assert names.lookup(['panic', 'craft', 'panic']) == [3, 0, 3]


def test_names_lookup_errors():
    '''Check Lookup function returns correct errors.'''
    names = Names()
    with pytest.raises(TypeError):
        names.lookup(1.4)
    with pytest.raises(TypeError):
        names.lookup([1.2])
    with pytest.raises(TypeError):
        names.lookup(['cart', 1.2])


def test_names_query():
    '''Check query function performs correctly.'''
    names = Names()
    names.lookup(['craft', 'arctic'])
    names.lookup(['arctic', 'town', 'craft'])
    names.lookup(['craft'])
    assert names.query('arctic') == 1
    assert names.query('ladel') is None


def test_names_query_errors():
    '''Check query function returns correct errors.'''
    names = Names()
    names.lookup(['craft', 'arctic', 'town'])
    with pytest.raises(TypeError):
        names.lookup(1)
    with pytest.raises(TypeError):
        names.lookup([1.2])
    with pytest.raises(TypeError):
        names.lookup(['cart', 1.2])


def test_names_get_string():
    '''Check get_string function performs correctly.'''
    names = Names()
    names.lookup(['craft', 'arctic', 'town'])
    assert names.get_name_string(2) == 'town'
    assert names.get_name_string(0) == 'craft'
    assert names.get_name_string(3) is None


def test_names_get_string_errors():
    '''Check get_string function returns correct errors.'''
    names = Names()
    with pytest.raises(TypeError):
        names.get_name_string('goat')
    with pytest.raises(TypeError):
        names.get_name_string(1.2)
    with pytest.raises(ValueError):
        names.get_name_string(-1)
