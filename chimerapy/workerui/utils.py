from typing import Optional
from chimerapy.engine.worker import Worker


def instantiate_worker(
    name: str,
    id: Optional[str] = None,
    delete_temp: bool = False,
    wport: int = 0,
) -> Worker:
    """Connect the worker to the manager."""
    worker = Worker(
        name=name,
        id=id,
        delete_temp=delete_temp,
        port=wport,
    )

    return worker
