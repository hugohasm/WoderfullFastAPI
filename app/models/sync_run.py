from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SyncRun(Base):
    __tablename__ = 'sync_runs'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='running')
    total_records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
