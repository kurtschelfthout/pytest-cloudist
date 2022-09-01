import pickle
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest
from _pytest.config import Config


def remote_initconfig(option_dict: dict, args):
    option_dict.setdefault("plugins", []).append("no:terminal")
    return Config.fromdictargs(option_dict, args)


def setup_config(config):
    config.option.usepdb = False
    config.option.cloudist = "no"


_ran_init_command = False


def run(
    init_command: Optional[str],
    option_dict: Dict[str, Any],
    nodeids: Union[str, List[str]],
) -> Tuple[List, List, List, List]:
    global _ran_init_command
    if not _ran_init_command and init_command:
        subprocess.run(init_command, shell=True, check=True)
        _ran_init_command = True

    args = [nodeids] if isinstance(nodeids, str) else nodeids
    config = remote_initconfig(option_dict, args)
    config.args = args
    setup_config(config)
    worker = Worker(config)
    config.pluginmanager.register(worker)
    config.hook.pytest_cmdline_main(config=config)
    return worker.messages


class Worker:
    def __init__(self, config):
        self.config = config
        self.messages: List[Tuple, Dict[str, Any]] = []

    @pytest.hookimpl
    def pytest_collectreport(self, report):
        # send only reports that have not passed to controller as optimization (pytest-xdist #330)
        if not report.passed:
            data = self.config.hook.pytest_report_to_serializable(
                config=self.config, report=report
            )
            self.messages.append(("failed_collect_report", data))

    @pytest.hookimpl
    def pytest_internalerror(self, excrepr):
        formatted_error = str(excrepr)
        self.messages.append(("internal_error", formatted_error))

    @pytest.hookimpl
    def pytest_warning_recorded(self, warning_message, when, nodeid, location):
        self.messages.append(
            (
                "warning",
                dict(
                    warning_message_data=serialize_warning_message(warning_message),
                    when=when,
                    nodeid=nodeid,
                    location=location,
                ),
            )
        )

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        self.messages.append(
            (
                "test_report",
                self.config.hook.pytest_report_to_serializable(
                    config=self.config, report=report
                ),
            )
        )


def serialize_warning_message(warning_message):
    if isinstance(warning_message.message, Warning):
        message_module = type(warning_message.message).__module__
        message_class_name = type(warning_message.message).__name__
        message_str = str(warning_message.message)
        try:
            pickle.dumps(warning_message.message.args)
        except pickle.PicklingError:
            message_args = None
        else:
            message_args = warning_message.message.args
    else:
        message_str = warning_message.message
        message_module = None
        message_class_name = None
        message_args = None
    if warning_message.category:
        category_module = warning_message.category.__module__
        category_class_name = warning_message.category.__name__
    else:
        category_module = None
        category_class_name = None

    result = {
        "message_str": message_str,
        "message_module": message_module,
        "message_class_name": message_class_name,
        "message_args": message_args,
        "category_module": category_module,
        "category_class_name": category_class_name,
    }
    # access private _WARNING_DETAILS because the attributes vary between Python versions
    for attr_name in warning_message._WARNING_DETAILS:
        if attr_name in ("message", "category"):
            continue
        attr = getattr(warning_message, attr_name)
        # Check if we can serialize the warning detail, marking `None` otherwise
        # Note that we need to define the attr (even as `None`) to allow deserializing
        try:
            pickle.dumps(attr)
        except pickle.PicklingError:
            result[attr_name] = repr(attr)
        else:
            result[attr_name] = attr
    return result
