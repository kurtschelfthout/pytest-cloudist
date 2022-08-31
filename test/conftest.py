import pytest


def pytest_addoption(parser) -> None:
    parser.addoption("--skip-slow", action="store_true", help="skip slow tests")


def pytest_collection_modifyitems(items, config):
    skip_slow = config.getoption("--skip-slow")

    marks = [
        (pytest.mark.slow, "slow", skip_slow, "--skip-slow"),
    ]
    for item in items:
        for (mark, kwd, skip_if_found, arg_name) in marks:
            if kwd in item.keywords:
                # If we're skipping, no need to actually add the marker or look for
                # other markers
                if skip_if_found:
                    item.add_marker(pytest.mark.skip(f"skipping due to {arg_name}"))
                    break

                item.add_marker(mark)
