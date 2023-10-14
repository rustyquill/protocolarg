import pytest
import simple_math

def test_add():
    assert simple_math.add(1, 2) == 3

def test_subtract():
    assert simple_math.subtract(1, 2) == -1

def test_multiply():
    assert simple_math.multiply(2, 3) == 6

def test_divide():
    assert simple_math.divide(10, 2) == 5
    with pytest.raises(ValueError):
        simple_math.divide(10, 0)
