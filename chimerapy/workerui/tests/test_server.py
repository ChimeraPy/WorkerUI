import asyncio
import tempfile

import pytest
from fastapi.testclient import TestClient

from chimerapy.engine.manager import Manager
from chimerapy.workerui.server import ChimeraPyWorkerUI
from chimerapy.workerui.tests.base_test import BaseTest


class TestServer(BaseTest):
    @pytest.fixture(scope="class")
    def event_loop(self):
        return asyncio.get_event_loop()

    @pytest.fixture(scope="class")
    def anyio_backend(self):
        return "asyncio"

    @pytest.fixture(scope="class")
    async def test_client_and_app(self, anyio_backend):
        app = ChimeraPyWorkerUI()
        client = TestClient(app)
        yield client, app

    @pytest.mark.anyio
    async def test_routes(self, test_client_and_app):
        test_client, app = test_client_and_app
        app_json = {"Content-Type": "application/json"}
        req_json = {
            "name": "worker1",
            "id": "worker1",
            "wport": 56403,
            "zeroconf": True,
            "timeout": 20,
            "ip": "",
            "port": 0,
            "delete_temp": True,
        }
        response = test_client.post("/start", headers=app_json, json=req_json)
        assert response.status_code == 200
        assert response.json() == await app._get_worker_state()
        response = test_client.post("/start", headers=app_json, json=req_json)
        assert response.status_code == 405

        # Create Manager
        m = Manager(logdir=tempfile.mkdtemp(), port=0)
        await m.aserve()
        await m.async_zeroconf(enable=True)

        # Connect Worker via Zeroconf
        response = test_client.post("/connect", headers=app_json, json=req_json)
        assert response.status_code == 200
        assert response.json() == await app._get_worker_state()
        assert response.json()["connected_to_manager"]
