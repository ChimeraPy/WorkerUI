from asyncio import Queue
from typing import Any, Dict, Optional

from chimerapy.engine.eventbus import EventBus, TypedObserver
from chimerapy.engine.worker import Worker


class StateUpdater:
    def __init__(self):
        self.clients = set()
        self.observers: Dict[str, TypedObserver] = {}
        self.eventbus: Optional[EventBus] = None
        self.worker: Optional[Worker] = None

    async def deinitialize(self):
        if self.eventbus is not None:
            for ob in self.observers.values():
                await self.eventbus.aunsubscribe(ob)
        self.observers = {}
        self.eventbus = None
        self.worker = None

    async def initialize(self, worker: Worker):

        self.eventbus = None
        self.worker = None

        self.eventbus = worker.eventbus
        self.observers = {
            "WorkerState.changed": TypedObserver(
                "WorkerState.changed",
                on_asend=self.on_worker_state_changed,
                handle_event="drop",
            )
        }

        for ob in self.observers.values():
            await self.eventbus.asubscribe(ob)

        self.worker = worker

    async def on_worker_state_changed(self):
        state = self.get_state()
        for client in self.clients:
            await client.put(state)

    async def broadcast_state(self):
        for client in self.clients:
            await client.put(self.get_state())

    async def add_client(self, client: Queue):
        self.clients.add(client)
        await client.put(self.get_state())

    async def remove_client(self, client: Queue):
        self.clients.discard(client)

    async def enqueue_sentinel(self):
        for client in self.clients:
            await client.put(None)

    def get_state(self) -> Dict[str, Any]:
        if self.worker is None:
            return {}

        state = self.worker.state.to_dict(encode_json=False)
        state["connected_to_manager"] = self.worker.http_client.connected_to_manager
        return state
