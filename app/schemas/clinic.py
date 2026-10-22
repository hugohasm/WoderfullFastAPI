from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ClinicBase(BaseModel):
    name: str
    location: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ClinicRead(ClinicBase):
    id: int
    name: str
    location: str | None = None
