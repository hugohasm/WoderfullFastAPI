from __future__ import annotations

from typing import Any

from sqlalchemy import func

from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.services.normalization import normalize_text


def similarity_score(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    a_norm = normalize_text(a)
    b_norm = normalize_text(b)
    if a_norm == b_norm:
        return 1.0
    if a_norm in b_norm or b_norm in a_norm:
        return 0.9
    return 0.0


def doctor_search_query(db, *, q: str, speciality: str | None = None, location: str | None = None, clinic: str | None = None, limit: int = 5):
    q_norm = normalize_text(q)
    stmt = db.query(Doctor).filter(Doctor.normalized_full_name % q_norm)
    if speciality:
        stmt = stmt.filter(Doctor.normalized_speciality.like(f'%{normalize_text(speciality)}%'))
    if location:
        stmt = stmt.filter(Doctor.normalized_location.like(f'%{normalize_text(location)}%'))
    if clinic:
        stmt = stmt.join(Clinic).filter(Clinic.normalized_name.like(f'%{normalize_text(clinic)}%'))
    stmt = stmt.order_by(func.similarity(Doctor.normalized_full_name, q_norm).desc())
    results = stmt.limit(limit).all()
    items = []
    for doctor in results:
        score = similarity_score(doctor.normalized_full_name, q_norm)
        items.append({
            'id': doctor.id,
            'name': doctor.full_name,
            'clinic': doctor.clinic.name if doctor.clinic else None,
            'speciality': doctor.speciality,
            'location': doctor.location,
            'match_score': score,
            'match_type': 'exact' if score >= 1 else 'trigram',
        })
    return items
