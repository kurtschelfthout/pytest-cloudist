import pytest


@pytest.hookimpl
def pytest_addoption(parser):
    group = parser.getgroup(
        "cloudist", "Distributed testing in the cloud using Meadowrun"
    )
    group.addoption(
        "--cloudist",
        metavar="distmode",
        action="store",
        choices=["test", "no"],
        dest="cloudist",
        default="no",
        help=(
            "set mode for distributing tests to workers.\n\n"
            "test: send each test to a worker separately.\n\n"
            "(default) no: run tests inprocess, don't distribute."
        ),
    )
    group.addoption(
        "--num-workers",
        dest="num_workers",
        metavar="num_workers",
        action="store",
        type=int,
        default=2,
        help="Number of workers to use for distributed testing.",
    )
    group.addoption(
        "--cpu",
        dest="logical_cpu_per_worker",
        metavar="logical_cpu_per_worker",
        action="store",
        type=float,
        default=1,
        help="The number of logical CPUs needed per worker.",
    )
    group.addoption(
        "--memory",
        dest="memory_gb_per_worker",
        metavar="memory_gb_per_worker",
        action="store",
        default=2.0,
        help="The amount of memory (in GiB) needed per worker.",
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    if config.getoption("cloudist") != "no" and not config.getvalue("collectonly"):
        from cloudist.cloud_session import CloudSession

        session = CloudSession(config)
        config.pluginmanager.register(session, "cloudsession")


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    usepdb = config.getoption("usepdb", False)  # a core option
    val = config.getvalue
    if not val("collectonly") and val("cloudist") != "no" and usepdb:
        raise pytest.UsageError("--pdb is incompatible with distributing tests.")
