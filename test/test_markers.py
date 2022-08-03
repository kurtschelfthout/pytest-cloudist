from time import sleep
import pytest


@pytest.mark.slow
def test_slow():
    assert True


@pytest.mark.db
def test_db():
    assert True


def test_no_marks():
    assert True
