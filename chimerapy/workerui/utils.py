from typing import Optional
from chimerapy.engine.worker import Worker

def instantiate_worker(
    name: str,
    id: Optional[str] = None,
    delete_temp: bool = False,
    port: int = 0,
    zeroconf: bool = False,
    ip: Optional[str] = None,
    wport: int = 0,
    timeout: int = 20,
) -> Worker:
    """Connect the worker to the manager."""
    method = "ip"
    if not zeroconf:
        if not ip or not port:
            raise ValueError("Must specify IP and port if not using zeroconf")
    else:
        method = "zeroconf"

    worker = Worker(
        name=name,
        id=id,
        delete_temp=delete_temp,
        port=wport,
    )

    worker.connect(
        port=port,
        host=ip,
        method=method,
        timeout=timeout,
    )

    return worker
