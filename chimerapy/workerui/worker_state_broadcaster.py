import asyncio
from typing import Dict, Optional

from chimerapy.engine.states import WorkerState
from chimerapy.engine.eventbus import TypedObserver, EventBus


class WorkerStateBroadcaster:
    def __init__(self):
        self.clients = set()
        self.observers: Dict[str, TypedObserver] = {}
        self.eventbus: Optional[EventBus] = None
        self.state: Optional[WorkerState] = None

    async def initialize(self, eventbus: EventBus, state: WorkerState):
        if self.eventbus is not None:
            for ob in self.observers.values():
                await self.eventbus.aunsubscribe(ob)

            self.state = None

        self.observers = {
            "WorkerState.changed": TypedObserver(
                "WorkerState.changed",
                on_asend=self.on_state_changed,
                handle_event="drop",
            )
        }

        self.eventbus = eventbus
        self.state = state

        for ob in self.observers.values():
            self.eventbus.subscribe(ob).result(timeout=1)

    async def on_state_changed(self):
        for client in self.clients:
            await client.put(self.state.to_dict(encode_json=False))

    async def add_client(self, q: asyncio.Queue):
        self.clients.add(q)

    async def remove_client(self, q: asyncio.Queue):
        self.clients.discard(q)

    async def enqueue_sentinel(self):
        for client in self.clients:
            await client.put(None)
