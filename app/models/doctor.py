from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Float, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.clinic import Clinic


class Doctor(Base):
    __tablename__ = 'doctors'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_record_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    speciality: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_speciality: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    clinic_id: Mapped[int | None] = mapped_column(ForeignKey('clinics.id'), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    county: Mapped[str | None] = mapped_column(String(128), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    education: Mapped[str | None] = mapped_column(Text, nullable=True)
    languages: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    clinic: Mapped['Clinic | None'] = relationship(back_populates='doctors')

    __table_args__ = (
        UniqueConstraint('source_record_key', name='uq_doctors_source_record_key'),
        Index('idx_doctors_name_trgm', 'normalized_full_name', postgresql_using='gin', postgresql_ops={'normalized_full_name': 'gin_trgm_ops'}),
        Index('idx_doctors_speciality_trgm', 'normalized_speciality', postgresql_using='gin', postgresql_ops={'normalized_speciality': 'gin_trgm_ops'}),
        Index('idx_doctors_location_trgm', 'normalized_location', postgresql_using='gin', postgresql_ops={'normalized_location': 'gin_trgm_ops'}),
    )
