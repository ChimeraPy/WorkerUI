import asyncio
import subprocess

import pytest

from chimerapy.engine.manager import Manager
from chimerapy.engine.utils import get_ip_address
from chimerapy.workerui.tests.base_test import BaseTest


class TestWorkerConnect(BaseTest):
    @pytest.fixture()
    async def manager(self):
        m = Manager(logdir="/tmp", port=9001)
        await m.aserve()
        await m.async_zeroconf(enable=True)

        yield m

        await m.async_shutdown()

    @pytest.mark.asyncio
    async def test_worker_connect(self, manager):
        command = ["cp-worker", "connect", "--name", "worker1", "--id", "worker1", "-z"]

        subprocess.Popen(command)
        await asyncio.sleep(5)
        assert manager.state.workers.get("worker1") is not None

        worker = manager.state.workers.get("worker1")
        assert worker.name == "worker1"
        assert worker.id == "worker1"
        assert worker.ip == get_ip_address()
        assert worker.nodes == {}

        command = [
            "cp-worker",
            "connect",
            "-n",
            "worker2",
            "--id",
            "worker2",
            "--ip",
            manager.state.ip,
            "-p",
            str(manager.state.port),
        ]
        subprocess.Popen(command)
        await asyncio.sleep(5)
        assert manager.state.workers.get("worker2") is not None

        worker = manager.state.workers.get("worker2")
        assert worker.name == "worker2"
        assert worker.id == "worker2"
        assert worker.ip == get_ip_address()
        assert worker.nodes == {}
