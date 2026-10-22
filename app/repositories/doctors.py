from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.services.normalization import normalize_text


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def _name_filter(self, value: str):
        nq = normalize_text(value)
        if not nq:
            return None
        tokens = [token for token in nq.split() if token]
        if not tokens:
            return None
        reversed_name = ' '.join(reversed(tokens))
        clauses = [
            Doctor.normalized_full_name.ilike(f'%{nq}%'),
            Doctor.normalized_full_name % nq,
            func.word_similarity(Doctor.normalized_full_name, nq) > 0.15,
            func.similarity(Doctor.normalized_full_name, nq) > 0.15,
        ]
        for token in tokens:
            clauses.append(Doctor.normalized_full_name.ilike(f'%{token}%'))
            clauses.append(Doctor.normalized_full_name % token)
        if reversed_name != nq:
            clauses.append(Doctor.normalized_full_name.ilike(f'%{reversed_name}%'))
            clauses.append(Doctor.normalized_full_name % reversed_name)
        return or_(*clauses)

    def get_by_id(self, doctor_id: int) -> Doctor | None:
        return self.db.get(Doctor, doctor_id)

    def list(self, *, name: str | None = None, speciality: str | None = None, location: str | None = None, clinic: str | None = None, language: str | None = None, min_rating: float | None = None, offset: int = 0, limit: int = 10):
        stmt = select(Doctor)
        conditions = []
        if name:
            name_filter = self._name_filter(name)
            if name_filter is not None:
                conditions.append(name_filter)
        if speciality:
            conditions.append(Doctor.normalized_speciality.ilike(f'%{normalize_text(speciality)}%'))
        if location:
            conditions.append(Doctor.normalized_location.ilike(f'%{normalize_text(location)}%'))
        if clinic:
            stmt = stmt.join(Doctor.clinic)
            conditions.append(Doctor.clinic.has(Doctor.clinic.property.mapper.class_.normalized_name.ilike(f'%{normalize_text(clinic)}%')))
        if language:
            conditions.append(Doctor.languages.ilike(f'%{normalize_text(language)}%'))
        if min_rating is not None:
            conditions.append(Doctor.rating >= min_rating)
        if conditions:
            stmt = stmt.where(or_(*conditions))
        if name:
            nq = normalize_text(name)
            stmt = stmt.order_by(
                func.word_similarity(Doctor.normalized_full_name, nq).desc(),
                func.similarity(Doctor.normalized_full_name, nq).desc(),
                Doctor.full_name.asc(),
            )
        else:
            stmt = stmt.order_by(Doctor.full_name.asc())
        stmt = stmt.offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def fuzzy_search(self, *, q: str, speciality: str | None = None, location: str | None = None, clinic: str | None = None, limit: int = 5):
        normalized = normalize_text(q)
        if not normalized:
            return []

        stmt = select(
            Doctor.id,
            Doctor.full_name,
            Doctor.speciality,
            Doctor.location,
            Doctor.rating,
            func.similarity(Doctor.normalized_full_name, normalized).label('match_score'),
            func.literal('trigram').label('match_type'),
            Doctor.clinic_id,
        )

        filters = [
            Doctor.normalized_full_name % normalized,
            func.word_similarity(Doctor.normalized_full_name, normalized) > 0.15,
            func.similarity(Doctor.normalized_full_name, normalized) > 0.15,
        ]
        if speciality:
            filters.append(Doctor.normalized_speciality.ilike(f'%{normalize_text(speciality)}%'))
        if location:
            filters.append(Doctor.normalized_location.ilike(f'%{normalize_text(location)}%'))
        if clinic:
            stmt = stmt.join(Doctor.clinic)
            filters.append(Doctor.clinic.has(Doctor.clinic.property.mapper.class_.normalized_name.ilike(f'%{normalize_text(clinic)}%')))

        stmt = stmt.where(or_(*filters))
        stmt = stmt.order_by(func.word_similarity(Doctor.normalized_full_name, normalized).desc(), func.similarity(Doctor.normalized_full_name, normalized).desc(), Doctor.full_name.asc()).limit(limit)
        return self.db.execute(stmt).all()
