from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.repositories.doctors import DoctorRepository
from app.schemas.doctor import DoctorDetail, DoctorRead
from app.services.normalization import normalize_text

router = APIRouter(prefix='/doctors', tags=['doctors'])


def _name_predicates(name: str):
    nq = normalize_text(name)
    if not nq:
        return []
    tokens = [t for t in nq.split() if t]
    if not tokens:
        return []
    predicates = [Doctor.normalized_full_name.ilike(f'%{tokens[0]}%')]
    if len(tokens) > 1:
        predicates.append(Doctor.normalized_full_name.ilike(f'%{tokens[-1]}%'))
        predicates.append(Doctor.normalized_full_name % tokens[-1])
        predicates.append(Doctor.normalized_full_name % tokens[0])
        reversed_name = ' '.join(reversed(tokens))
        predicates.append(Doctor.normalized_full_name.ilike(f'%{reversed_name}%'))
        predicates.append(Doctor.normalized_full_name % reversed_name)
    return predicates


@router.get('', response_model=list[DoctorRead])
def list_doctors(
    name: str | None = None,
    speciality: str | None = Query(default=None, alias='speciality'),
    location: str | None = None,
    clinic: str | None = None,
    language: str | None = None,
    min_rating: float | None = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Doctor)
    if name:
        nq = normalize_text(name)
        name_predicates = _name_predicates(name)
        if name_predicates:
            query = query.filter(or_(*name_predicates))
        query = query.order_by(
            func.similarity(Doctor.normalized_full_name, nq).desc(),
            func.word_similarity(Doctor.normalized_full_name, nq).desc(),
            Doctor.full_name.asc(),
        )
    if speciality:
        query = query.filter(Doctor.normalized_speciality.ilike(f'%{normalize_text(speciality)}%'))
    if location:
        query = query.filter(Doctor.normalized_location.ilike(f'%{normalize_text(location)}%'))
    if clinic:
        query = query.join(Clinic).filter(Clinic.normalized_name.ilike(f'%{normalize_text(clinic)}%'))
    if language:
        query = query.filter(Doctor.languages.ilike(f'%{normalize_text(language)}%'))
    if min_rating is not None:
        query = query.filter(Doctor.rating >= min_rating)

    items = query.offset(offset).limit(limit).all()
    return [DoctorRead(
        id=item.id,
        full_name=item.full_name,
        speciality=item.speciality,
        clinic=item.clinic.name if item.clinic else None,
        location=item.location,
        phone=item.phone,
        email=item.email,
        rating=item.rating,
    ) for item in items]


@router.get('/{doctor_id}', response_model=DoctorDetail)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = DoctorRepository(db).get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail='Doctor not found')
    return DoctorDetail(
        id=doctor.id,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        full_name=doctor.full_name,
        speciality=doctor.speciality,
        clinic=doctor.clinic.name if doctor.clinic else None,
        location=doctor.location,
        address=doctor.address,
        phone=doctor.phone,
        email=doctor.email,
        postal_code=doctor.postal_code,
        county=doctor.county,
        years_experience=doctor.years_experience,
        education=doctor.education,
        languages=(doctor.languages.split('|') if doctor.languages else []),
        availability=doctor.availability,
        rating=doctor.rating,
        created_at=doctor.created_at,
        updated_at=doctor.updated_at,
    )
