from pathlib import Path

from typing import Dict, Any, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from chimerapy.workerui.models import WorkerConfig
from chimerapy.workerui.utils import instantiate_worker
import asyncio
from chimerapy.engine.worker import Worker
from chimerapy.workerui.worker_state_broadcaster import WorkerStateBroadcaster
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState


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
        self._serve_static_files()
        self.worker_instance: Optional[Worker] = None
        self.updates_broadcaster: Optional[WorkerStateBroadcaster] = None
        self._add_routes()

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
        self.add_websocket_route("/updates", self._handle_updates)

    async def _get_worker_state(self) -> Dict[str, bool]:
        return self.worker_instance.state.to_dict() if self.worker_instance else {}

    async def _instantiate_worker(self, config: WorkerConfig) -> Dict[str, Any]:
        if self.worker_instance is not None:
            # Method Not Allowed
            raise HTTPException(
                status_code=405,
                detail="Worker already instantiated. Please restart the server.",
            )

        self.worker_instance = instantiate_worker(
            name=config.name,
            id=config.id,
            wport=config.wport,
            delete_temp=config.delete_temp,
            port=config.port,
            ip=config.ip,
            zeroconf=config.zeroconf,
        )
        # await self._initialize_updater()
        return self.worker_instance.state.to_dict(encode_json=False)

    async def _initialize_updater(self):
        if self.worker_instance is not None:
            await self.updates_broadcaster.initialize()

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


def create_worker_ui_app():
    return ChimeraPyWorkerUI()
