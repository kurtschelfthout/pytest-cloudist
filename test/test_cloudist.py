from time import sleep
import warnings

SLEEP = 10


def test_one():
    sleep(SLEEP)
    assert 1 == 1


def test_two():
    sleep(SLEEP)
    warnings.warn("This is a warning", DeprecationWarning)
    assert 1 == 1


def test_three():
    sleep(SLEEP)
    assert 1 == 2


def test_four():
    sleep(SLEEP)
    assert 1 == 1


# def test_five():
#     sleep(SLEEP)
#     assert 1 == 1
