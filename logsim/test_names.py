#tests for names moduele
import pytest
from names import Names

def test_names_lookup():
    names=Names()
    assert names.lookup(['craft','arctic'])==[0,1]
    assert names.lookup(['arctic','town','craft'])==[1,2,0]
    assert names.lookup(['craft'])==[0]



def test_names_lookup_errors():
    names=Names()
    with pytest.raises(TypeError):
        names.lookup(1.4)
    with pytest.raises(TypeError):
        names.lookup([1.2])
    with pytest.raises(TypeError):
        names.lookup(['cart',1.2])
    