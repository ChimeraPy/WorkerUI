import asyncio
from concurrent.futures import TimeoutError
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState

from chimerapy.engine.worker import Worker
from chimerapy.workerui.models import WorkerConfig
from chimerapy.workerui.state_updater import StateUpdater
from chimerapy.workerui.utils import instantiate_worker

STATIC_DIR = Path(__file__).parent / "build"


async def relay(q: asyncio.Queue, ws: WebSocket, is_sentinel) -> None:
    """Relay messages from the queue to the websocket."""
    while True:
        message = await q.get()
        if ws.client_state == WebSocketState.DISCONNECTED:
            break
        if message is None:
            break
        if is_sentinel(message):  # Received Sentinel
            break
        try:
            await ws.send_json({"data": message})
        except WebSocketDisconnect:
            break


async def poll(ws: WebSocket) -> None:
    """Continuously poll the websocket for messages."""
    while True:
        try:
            await ws.receive_json()  # FixMe: What is the best way of polling?
        except WebSocketDisconnect:
            break


async def _connect_to_manager(worker_instance: Worker, config: WorkerConfig) -> bool:
    """Connect the worker to the manager."""
    success = await worker_instance.async_connect(
        port=config.port,
        host=config.ip,
        timeout=config.timeout,
        method="zeroconf" if config.zeroconf else "ip",
    )

    return success


class ChimeraPyWorkerUI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_instance: Optional[Worker] = None
        self.state_updater = StateUpdater()
        self._add_routes()
        # self._serve_static_files()

    def _serve_static_files(self):
        if STATIC_DIR.exists():
            self.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
            self.mount("/_app", StaticFiles(directory=STATIC_DIR / "_app"), name="_app")
            self.add_api_route(
                "/", lambda: RedirectResponse(url="static"), methods=["GET"]
            )

    def _add_routes(self):
        self.add_api_route("/state", self._get_worker_state, methods=["GET"])
        self.add_api_route("/start", self._start_worker, methods=["POST"])
        self.add_api_route("/connect", self._connect_worker, methods=["POST"])
        self.add_api_route("/disconnect", self._disconnect_worker, methods=["POST"])
        self.add_api_route("/shutdown", self._shutdown_worker, methods=["POST"])
        self.add_websocket_route("/updates", self._update_state)

    async def _get_worker_state(self) -> Dict[str, Any]:
        state = (
            self.worker_instance.state.to_dict(encode_json=False)
            if self.worker_instance
            else {}
        )
        if self.worker_instance:
            state["connected_to_manager"] = self._is_worker_connected()
        return state

    async def _connect_worker(self, config: WorkerConfig) -> Dict[str, Any]:
        if self.worker_instance is None:
            raise HTTPException(
                status_code=404,
                detail="Worker not instantiated. Please instantiate the worker first.",
            )

        success = await _connect_to_manager(self.worker_instance, config)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Connection to manager failed. "
                "Please retry when the manager is running.",
            )

        await self.state_updater.broadcast_state()

        return await self._get_worker_state()

    async def _disconnect_worker(self) -> Dict[str, Any]:
        can, reason = await self._can_shutdown_or_disconnect()

        if not can:
            raise HTTPException(status_code=409, detail=reason)

        else:
            assert self.worker_instance is not None
            await self.worker_instance.async_deregister()
            await self.state_updater.broadcast_state()
            return await self._get_worker_state()

    async def _start_worker(self, config: WorkerConfig) -> Dict[str, Any]:
        if self.worker_instance is not None:
            # Method Not Allowed
            raise HTTPException(
                status_code=405,
                detail="Worker already instantiated. Please restart the server.",
            )

        self.worker_instance = instantiate_worker(
            name=config.name,
            id=config.id or None,
            wport=config.wport or 0,
            delete_temp=config.delete_temp,
        )

        await self.worker_instance.aserve()
        await self.state_updater.deinitialize()
        await self.state_updater.initialize(self.worker_instance)
        await self.state_updater.broadcast_state()

        return await self._get_worker_state()

    async def _can_shutdown_or_disconnect(self) -> Tuple[bool, str]:
        if self.worker_instance is None:
            return False, "Worker not instantiated."
        if len(self.worker_instance.state.nodes) > 0:
            return False, "Worker has active nodes."

        return True, "Worker can be shutdown."

    async def _shutdown_worker(self) -> Dict[str, Any]:
        can, reason = await self._can_shutdown_or_disconnect()
        if not can:
            raise HTTPException(status_code=409, detail=reason)
        else:
            assert self.worker_instance is not None
            await self.state_updater.deinitialize()
            await self.worker_instance.async_shutdown()
            await self.state_updater.broadcast_state()
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
            return await self._get_worker_state()
        except TimeoutError as e:
            raise HTTPException(
                status_code=408, detail="Connection to manager timed out."
            ) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def _update_state(self, websocket: WebSocket):
        await websocket.accept()
        update_queue: asyncio.Queue = asyncio.Queue()

        relay_task = asyncio.create_task(
            relay(update_queue, websocket, is_sentinel=lambda m: m is None)
        )

        poll_task = asyncio.create_task(poll(websocket))
        await self.state_updater.add_client(update_queue)
        try:
            done, pending = await asyncio.wait(
                [relay_task, poll_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        finally:
            await self.state_updater.remove_client(update_queue)
            # await websocket.close()

    def _is_worker_connected(self) -> bool:
        if self.worker_instance is not None:
            return self.worker_instance.http_client.connected_to_manager

        return False


def create_worker_ui_app():
    return ChimeraPyWorkerUI()
