from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.repositories.doctors import DoctorRepository
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.normalization import normalize_text

router = APIRouter(tags=['search'])


@router.post('/search', response_model=SearchResponse)
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    if payload.entity_type == 'clinic':
        q = payload.name or ''
        query = db.query(Clinic)
        if q:
            nq = normalize_text(q)
            query = query.filter(or_(Clinic.normalized_name.ilike(f'%{nq}%'), Clinic.normalized_location.ilike(f'%{nq}%')))
        items = query.order_by(Clinic.name.asc()).limit(payload.limit or 5).all()
        return SearchResponse(results=[SearchResult(id=item.id, name=item.name, location=item.location, match_score=1.0, match_type='exact') for item in items], total=len(items), needs_clarification=False)

    q = payload.name or ''
    filters = payload.filters or {}
    query = db.query(Doctor)
    if q:
        nq = normalize_text(q)
        if nq:
            query = query.filter(
                or_(
                    Doctor.normalized_full_name.ilike(f'%{nq}%'),
                    Doctor.normalized_full_name % nq,
                    func.similarity(Doctor.normalized_full_name, nq) > 0.15,
                    func.word_similarity(Doctor.normalized_full_name, nq) > 0.15,
                )
            )
    if filters.get('location'):
        query = query.filter(Doctor.normalized_location.ilike(f'%{normalize_text(filters["location"])}%'))
    if filters.get('speciality'):
        query = query.filter(Doctor.normalized_speciality.ilike(f'%{normalize_text(filters["speciality"])}%'))
    items = query.order_by(
        func.word_similarity(Doctor.normalized_full_name, nq if q else '').desc(),
        func.similarity(Doctor.normalized_full_name, nq if q else '').desc(),
        Doctor.full_name.asc(),
    ).limit(payload.limit or 5).all()
    results = []
    for doctor in items:
        score = 1.0 if normalize_text(doctor.full_name) == normalize_text(q) else 0.8
        if q and normalize_text(q):
            score = max(
                score,
                float(func.similarity(Doctor.normalized_full_name, normalize_text(q)).label('x')) if False else 0.0,
            )
        results.append(SearchResult(id=doctor.id, name=doctor.full_name, clinic=doctor.clinic.name if doctor.clinic else None, speciality=doctor.speciality, location=doctor.location, match_score=score, match_type='exact' if score >= 1.0 else 'trigram'))
    return SearchResponse(results=results, total=len(results), needs_clarification=False)
