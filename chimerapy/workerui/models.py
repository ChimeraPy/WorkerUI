from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkerConfig(BaseModel):
    """Configuration for the chimerapy worker creation"""

    name: str = Field(
        ...,
        description="Name of the worker",
    )

    wport: int = Field(
        default=0,
        description="Port to serve the worker on",
    )

    delete_temp: bool = Field(
        default=False,
        description="Delete temporary files after processing",
    )

    id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the chimerapy worker",
    )

    zeroconf: bool = Field(
        default=False,
        description="Use zeroconf to find the manager",
    )

    ip: Optional[str] = Field(
        default=None,
        description="IP address of the manager",
    )

    port: Optional[int] = Field(
        default=None,
        description="Port of the manager",
    )

    timeout: int = Field(
        default=20,
        description="Timeout for the worker",
    )

    model_config = ConfigDict(
        frozen=False,
        extra="forbid",
    )
