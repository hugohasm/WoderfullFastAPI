from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.doctor import Doctor


class Clinic(Base):
    __tablename__ = 'clinics'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    doctors: Mapped[list['Doctor']] = relationship(back_populates='clinic')

    __table_args__ = (
        Index('idx_clinics_name_trgm', 'normalized_name', postgresql_using='gin', postgresql_ops={'normalized_name': 'gin_trgm_ops'}),
        Index('idx_clinics_location_trgm', 'normalized_location', postgresql_using='gin', postgresql_ops={'normalized_location': 'gin_trgm_ops'}),
    )
