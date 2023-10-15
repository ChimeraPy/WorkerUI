import asyncio
from concurrent.futures import TimeoutError
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from chimerapy.engine.worker import Worker
from chimerapy.workerui.models import WorkerConfig
from chimerapy.workerui.utils import instantiate_worker

STATIC_DIR = Path(__file__).parent / "build"


class ChimeraPyWorkerUI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_instance: Optional[Worker] = None
        self._add_routes()
        self._serve_static_files()

    def _serve_static_files(self):
        if STATIC_DIR.exists():
            self.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
            self.mount("/_app", StaticFiles(directory=STATIC_DIR / "_app"), name="_app")
            self.add_api_route(
                "/", lambda: RedirectResponse(url="static"), methods=["GET"]
            )

    def _add_routes(self):
        self.add_api_route("/state", self._get_worker_state, methods=["GET"])
        self.add_api_route("/connect", self._instantiate_worker, methods=["POST"])
        self.add_api_route("/shutdown", self._shutdown_worker, methods=["POST"])

    async def _get_worker_state(self) -> Dict[str, Any]:
        return (
            self.worker_instance.state.to_dict(encode_json=False)
            if self.worker_instance
            else {}
        )

    async def _instantiate_worker(self, config: WorkerConfig) -> Dict[str, Any]:
        if self.worker_instance is not None:
            # Method Not Allowed
            raise HTTPException(
                status_code=405,
                detail="Worker already instantiated. Please restart the server.",
            )
        try:
            self.worker_instance = instantiate_worker(
                name=config.name,
                id=config.id or None,
                wport=config.wport or 0,
                delete_temp=config.delete_temp,
            )
            await self.worker_instance.aserve()

            await self.worker_instance.async_connect(
                port=config.port,
                host=config.ip,
                timeout=config.timeout,
                method="zeroconf" if config.zeroconf else "ip",
            )
            print("Worker connected to manager.")
        except TimeoutError:
            self.worker_instance = None
            raise HTTPException(  # noqa: B904
                status_code=408, detail="Connection to manager timed out."
            )
        except Exception as e:
            self.worker_instance = None
            print(e)
            raise HTTPException(status_code=500, detail=str(e))  # noqa: B904

        return await self._get_worker_state()

    async def _can_shutdown_worker(self) -> Tuple[bool, str]:
        if self.worker_instance is None:
            return False, "Worker not instantiated."
        if len(self.worker_instance.state.nodes) > 0:
            return False, "Worker has active nodes."

        return True, "Worker can be shutdown."

    async def _shutdown_worker(self) -> Dict[str, Any]:
        can, reason = await self._can_shutdown_worker()
        if not can:
            raise HTTPException(status_code=409, detail=reason)
        else:
            assert self.worker_instance is not None
            await self.worker_instance.async_shutdown()
            self.worker_instance = None
            return {}

    async def _connect_to_manager(self, config: WorkerConfig) -> Dict[str, Any]:
        if self.worker_instance is None:
            raise HTTPException(status_code=404, detail="Worker not instantiated.")

        if self._is_worker_connected():
            raise HTTPException(
                status_code=409, detail="Worker already connected to manager."
            )

        try:
            await self.worker_instance.async_connect(
                port=config.port,
                host=config.ip,
                timeout=config.timeout,
                method="zeroconf" if config.zeroconf else "ip",
            )
        except TimeoutError:
            raise HTTPException(
                status_code=408, detail="Connection to manager timed out."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _is_worker_connected(self) -> bool:
        if self.worker_instance is not None:
            return self.worker_instance.http_client.connected_to_manager

        return False


def create_worker_ui_app():
    return ChimeraPyWorkerUI()
