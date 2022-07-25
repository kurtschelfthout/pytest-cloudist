import asyncio
import os
from pprint import pprint
import sys
from meadowrun import (
    AllocCloudInstances,
    Deployment,
    run_map,
)
from cdist.remote_function import run
import pytest


class CloudSession:
    """A pytest plugin which runs a distributed test session in the cloud."""

    def __init__(self, config):
        self.config = config

    async def meadowrun_map(self, items):
        num_workers = self.config.option.num_workers
        cpu_per_worker = self.config.option.logical_cpu_per_worker
        memory_gb_per_worker = self.config.option.memory_gb_per_worker
        node_ids = [item.nodeid for item in items]
        results = await run_map(
            run,
            node_ids,
            AllocCloudInstances(
                cloud_provider="EC2",
                interruption_probability_threshold=80,
                logical_cpu_required_per_task=cpu_per_worker,
                memory_gb_required_per_task=memory_gb_per_worker,
                num_concurrent_tasks=num_workers,
            ),
            await Deployment.mirror_local(),
        )
        for result in results:
            for tag, data in result:
                if tag == "test_report":
                    report = self.config.hook.pytest_report_from_serializable(
                        config=self.config, data=data
                    )
                    self.config.hook.pytest_runtest_logreport(report=report)
                elif tag == "internal_error":
                    try:
                        assert False, data
                    except AssertionError:
                        from _pytest._code import ExceptionInfo

                        excinfo = ExceptionInfo.from_current()
                        excrepr = excinfo.getrepr()
                        self.config.hook.pytest_internalerror(
                            excrepr=excrepr, excinfo=excinfo
                        )
                elif tag == "warning":
                    kwargs = dict(
                        warning_message=deserialize_warning_message(
                            data["warning_message_data"]
                        ),
                        when=data["when"],
                        nodeid=data["nodeid"],
                        location=data["location"],
                    )
                    self.config.hook.pytest_warning_recorded.call_historic(
                        kwargs=kwargs
                    )
                elif tag == "failed_collect_report":
                    report = self.config.hook.pytest_report_from_serializable(
                        config=self.config, data=data
                    )
                    self.config.hook.pytest_collectreport(report=report)

    @pytest.hookimpl
    def pytest_runtestloop(self, session):
        asyncio.run(self.meadowrun_map(session.items))
        return True


def deserialize_warning_message(data):
    import warnings
    import importlib

    if data["message_module"]:
        mod = importlib.import_module(data["message_module"])
        cls = getattr(mod, data["message_class_name"])
        message = None
        if data["message_args"] is not None:
            try:
                message = cls(*data["message_args"])
            except TypeError:
                pass
        if message is None:
            # could not recreate the original warning instance;
            # create a generic Warning instance with the original
            # message at least
            message_text = "{mod}.{cls}: {msg}".format(
                mod=data["message_module"],
                cls=data["message_class_name"],
                msg=data["message_str"],
            )
            message = Warning(message_text)
    else:
        message = data["message_str"]

    if data["category_module"]:
        mod = importlib.import_module(data["category_module"])
        category = getattr(mod, data["category_class_name"])
    else:
        category = None

    kwargs = {"message": message, "category": category}
    # access private _WARNING_DETAILS because the attributes vary between Python versions
    for attr_name in warnings.WarningMessage._WARNING_DETAILS:  # type: ignore[attr-defined]
        if attr_name in ("message", "category"):
            continue
        kwargs[attr_name] = data[attr_name]

    return warnings.WarningMessage(**kwargs)  # type: ignore[arg-type]
