from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.clinics import ClinicRepository
from app.schemas.clinic import ClinicRead

router = APIRouter(prefix='/clinics', tags=['clinics'])


@router.get('', response_model=list[ClinicRead])
def list_clinics(
    name: str | None = None,
    location: str | None = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    repo = ClinicRepository(db)
    items = repo.list(name=name, location=location, offset=offset, limit=limit)
    return [ClinicRead(id=item.id, name=item.name, location=item.location) for item in items]


@router.get('/{clinic_id}', response_model=ClinicRead)
def get_clinic(clinic_id: int, db: Session = Depends(get_db)):
    clinic = ClinicRepository(db).get_by_id(clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail='Clinic not found')
    return ClinicRead(id=clinic.id, name=clinic.name, location=clinic.location)
