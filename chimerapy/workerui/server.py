from pathlib import Path

from typing import Dict, Any, Optional, Tuple
from concurrent.futures import TimeoutError
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from chimerapy.workerui.models import WorkerConfig
from chimerapy.workerui.utils import instantiate_worker
import asyncio
from chimerapy.engine.worker import Worker
from chimerapy.workerui.worker_state_broadcaster import WorkerStateBroadcaster
from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState


async def relay(
    q: asyncio.Queue, ws: WebSocket, is_sentinel, signal: str = "update"
) -> None:
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
            await ws.send_json({"signal": signal, "data": message})
        except WebSocketDisconnect:
            break


async def poll(ws: WebSocket) -> None:
    """Continuously poll the websocket for messages."""
    while True:
        try:
            await ws.receive_json()  # FixMe: What is the best way of polling?
        except WebSocketDisconnect:
            break


STATIC_DIR = Path(__file__).parent / "build"


class ChimeraPyWorkerUI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_instance: Optional[Worker] = None
        self.updates_broadcaster: Optional[
            WorkerStateBroadcaster
        ] = WorkerStateBroadcaster()
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
        self.add_websocket_route("/updates", self._handle_updates)

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
            print("Connected to manager.")
            await self._initialize_updater()
        except TimeoutError as e:
            raise e
            self.worker_instance = None
            raise HTTPException(
                status_code=408, detail="Connection to manager timed out."
            )
        except Exception as e:
            self.worker_instance = None
            raise HTTPException(status_code=500, detail=str(e))

        return self.worker_instance.state.to_dict(encode_json=False)

    async def _initialize_updater(self):
        if self.worker_instance is not None:
            await self.updates_broadcaster.initialize(
                state=self.worker_instance.state, eventbus=self.worker_instance.eventbus
            )

    async def _handle_updates(self, ws: WebSocket) -> None:
        await ws.accept()

        if self.updates_broadcaster is None:
            await ws.send_json(
                {"signal": "error", "data": {"Worker not instantiated."}}
            )

        if self.updates_broadcaster is not None:
            update_queue: asyncio.Queue = asyncio.Queue()
            relay_task = asyncio.create_task(
                relay(
                    q=update_queue,
                    ws=ws,
                    is_sentinel=lambda message: message is None,
                    signal="update",
                )
            )
            poll_task = asyncio.create_task(poll(ws))

            try:
                done, pending = await asyncio.wait(
                    [relay_task, poll_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
            finally:
                await self.updates_broadcaster.remove_client(update_queue)
                await ws.close()

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


def create_worker_ui_app():
    return ChimeraPyWorkerUI()
