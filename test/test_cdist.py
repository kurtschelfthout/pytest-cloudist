from time import sleep
import warnings


def test_one():
    sleep(1)
    assert 1 == 1


def test_two():
    sleep(1)
    warnings.warn("This is a warning", DeprecationWarning)
    assert 1 == 1


def test_three():
    sleep(1)
    assert 1 == 2


def test_four():
    sleep(1)
    assert 1 == 1


def test_five():
    sleep(1)
    assert 1 == 1
