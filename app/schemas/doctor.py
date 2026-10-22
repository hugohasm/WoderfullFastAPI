from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class DoctorBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    clinic_name: Optional[str] = None
    location: Optional[str] = None
    speciality: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    postal_code: Optional[str] = None
    county: Optional[str] = None
    years_experience: Optional[int] = None
    education: Optional[str] = None
    languages: list[str] = Field(default_factory=list)
    availability: Optional[str] = None
    rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class DoctorRecord(DoctorBase):
    pass


class DoctorRead(BaseModel):
    id: int
    full_name: str
    speciality: Optional[str]
    clinic: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    rating: Optional[float]
    match_score: Optional[float] = None
    match_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DoctorDetail(DoctorRead):
    first_name: Optional[str]
    last_name: Optional[str]
    address: Optional[str]
    postal_code: Optional[str]
    county: Optional[str]
    education: Optional[str]
    languages: list[str]
    availability: Optional[str]
    years_experience: Optional[int]
    created_at: datetime
    updated_at: datetime
