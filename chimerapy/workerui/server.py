from pathlib import Path

from typing import Dict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from chimerapy.workerui.models import WorkerConfig


STATIC_DIR = Path(__file__).parent / "build"


class ChimeraPyWorkerUI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._serve_static_files()
        self.worker_instance = None
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

    async def _get_worker_state(self) -> Dict[str, bool]:
        return self.worker_instance.state.to_dict() if self.worker_instance else {}

    async def _instantiate_worker(self, config: WorkerConfig) -> Dict[str, bool]:
        pass


def create_worker_ui_app():
    return ChimeraPyWorkerUI()
