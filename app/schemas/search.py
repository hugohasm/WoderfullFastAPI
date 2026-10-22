from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    entity_type: Literal['doctor', 'clinic'] = 'doctor'
    name: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = 5

    model_config = ConfigDict(extra='ignore')


class SearchResult(BaseModel):
    id: int | str
    name: str
    clinic: str | None = None
    speciality: str | None = None
    location: str | None = None
    match_score: float | None = None
    match_type: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    needs_clarification: bool = False
