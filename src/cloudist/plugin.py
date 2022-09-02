#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:

#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import pytest


@pytest.hookimpl
def pytest_addoption(parser):
    group = parser.getgroup(
        "cloudist", "Distributed testing in the cloud using Meadowrun"
    )
    group.addoption(
        "--cloudist",
        action="store",
        choices=["test", "file", "no"],
        dest="cloudist",
        default="no",
        help=(
            "Set mode for distributing tests to workers.\n\n"
            "test: send each test to a worker separately.\n\n"
            "file: send each test file to a worker separately.\n\n"
            "(default) no: run tests inprocess, don't distribute."
        ),
    )
    group.addoption(
        "--cd-tasks-per-worker-target",
        action="store",
        dest="tasks_per_worker_target",
        metavar="tasks_per_worker_target",
        type=int,
        default=-1,
        help=(
            "The number of tasks to target per worker. "
            "This number determines whether individual tests or files are grouped and sent as a chunk to the test worker. "
            "Chunking is normally more efficient, but may affect load balancing and worsen the effect of stragglers."
        ),
    )
    group.addoption(
        "--cd-num-workers",
        dest="num_workers",
        metavar="num_workers",
        action="store",
        type=int,
        default=2,
        help="Number of workers to use for distributed testing.",
    )
    group.addoption(
        "--cd-cpu-per-worker",
        dest="logical_cpu_per_worker",
        metavar="logical_cpu_per_worker",
        action="store",
        type=float,
        default=1,
        help="The number of logical CPUs needed per worker.",
    )
    group.addoption(
        "--cd-memory-per-worker",
        dest="memory_gb_per_worker",
        metavar="memory_gb_per_worker",
        action="store",
        type=float,
        default=2.0,
        help="The amount of memory (in GiB) needed per worker.",
    )
    group.addoption(
        "--cd-interrupt-prob",
        dest="interruption_probability_threshold",
        action="store",
        default=80,
        help="The estimated probability that spot instances are interrupted by AWS. Set to 0 for on-demand instances, which will be up to 10x more expensive.",
    )
    group.addoption(
        "--cd-extra-files",
        dest="extra_files",
        action="append",
        help="Extra files to copy as to the remote machines, if needed. .py files on sys.path are copied automatically.",
    )
    group.addoption(
        "--cd-init-command",
        dest="init_command",
        action="store",
        help="Initialization command to run once per worker",
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    if config.getoption("cloudist") != "no" and not config.getvalue("collectonly"):
        from cloudist.meadowrun_session import MeadowrunSession

        session = MeadowrunSession(config)
        config.pluginmanager.register(session, "meadowrunsession")


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    usepdb = config.getoption("usepdb", False)  # a core option
    val = config.getvalue
    if not val("collectonly") and val("cloudist") != "no" and usepdb:
        raise pytest.UsageError("--pdb is incompatible with distributing tests.")
