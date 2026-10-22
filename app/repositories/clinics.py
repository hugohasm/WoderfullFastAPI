from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clinic import Clinic


class ClinicRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, clinic_id: int) -> Clinic | None:
        return self.db.get(Clinic, clinic_id)

    def list(self, *, name: str | None = None, location: str | None = None, offset: int = 0, limit: int = 10):
        stmt = select(Clinic)
        conditions = []
        if name:
            conditions.append(Clinic.normalized_name.ilike(f'%{name.lower()}%'))
        if location:
            conditions.append(Clinic.normalized_location.ilike(f'%{location.lower()}%'))
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(Clinic.name.asc()).offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def fuzzy_search(self, *, q: str, limit: int = 5):
        stmt = select(Clinic).where(Clinic.normalized_name % q.lower()).order_by(Clinic.normalized_name).limit(limit)
        return self.db.execute(stmt).scalars().all()
