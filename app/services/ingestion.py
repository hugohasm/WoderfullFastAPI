from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.sync_run import SyncRun
from app.services.normalization import build_full_name, build_record_key, normalize_text


settings = get_settings()


class IngestionError(RuntimeError):
    pass


def ensure_pg_extensions(db: Session) -> None:
    db.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    db.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    db.commit()


def load_records_from_file(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    with target.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise IngestionError('Upstream response is empty or invalid.')
    return data


def fetch_upstream_records(url: str | None = None) -> list[dict[str, Any]]:
    source = url or settings.upstream_api_url
    if source.startswith('http'):
        response = httpx.get(source, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
    else:
        payload = load_records_from_file(source)

    if not isinstance(payload, list) or not payload:
        raise IngestionError('Upstream response is empty or invalid.')
    return payload


def upsert_clinic(db: Session, data: dict[str, Any]) -> Clinic:
    clinic_name = str(data.get('clinic_name') or '').strip()
    location = str(data.get('location') or '').strip()
    if not clinic_name:
        return None
    clinic = db.execute(select(Clinic).where(Clinic.name == clinic_name, Clinic.location == location)).scalars().first()
    if clinic is None:
        clinic = Clinic(name=clinic_name, location=location, normalized_name=normalize_text(clinic_name), normalized_location=normalize_text(location))
        db.add(clinic)
        db.flush()
    else:
        clinic.name = clinic_name
        clinic.location = location
        clinic.normalized_name = normalize_text(clinic_name)
        clinic.normalized_location = normalize_text(location)
        clinic.updated_at = datetime.utcnow()
    return clinic


def ingest_records(db: Session, records: list[dict[str, Any]]) -> dict[str, int]:
    if not records:
        raise IngestionError('No records to ingest.')

    processed = 0
    rejected = 0
    created = 0

    for item in records:
        if not isinstance(item, dict):
            rejected += 1
            continue
        if not item.get('first_name') and not item.get('last_name'):
            rejected += 1
            continue

        clinic = upsert_clinic(db, item)
        full_name = build_full_name(item.get('first_name'), item.get('last_name'))
        record_key = build_record_key(item)

        doctor = db.execute(select(Doctor).where(Doctor.source_record_key == record_key)).scalars().first()
        if doctor is None:
            doctor = Doctor(
                source_record_key=record_key,
                first_name=item.get('first_name'),
                last_name=item.get('last_name'),
                full_name=full_name,
                normalized_full_name=normalize_text(full_name),
                speciality=item.get('speciality'),
                normalized_speciality=normalize_text(item.get('speciality')),
                clinic_id=clinic.id if clinic else None,
                location=item.get('location'),
                normalized_location=normalize_text(item.get('location')),
                address=item.get('address'),
                phone=item.get('phone'),
                email=(item.get('email') or '').strip() or None,
                postal_code=item.get('postal_code'),
                county=item.get('county'),
                years_experience=item.get('years_experience'),
                education=item.get('education'),
                languages='|'.join(item.get('languages') or []),
                availability=item.get('availability'),
                rating=item.get('rating'),
            )
            db.add(doctor)
            created += 1
        else:
            doctor.first_name = item.get('first_name')
            doctor.last_name = item.get('last_name')
            doctor.full_name = full_name
            doctor.normalized_full_name = normalize_text(full_name)
            doctor.speciality = item.get('speciality')
            doctor.normalized_speciality = normalize_text(item.get('speciality'))
            doctor.clinic_id = clinic.id if clinic else None
            doctor.location = item.get('location')
            doctor.normalized_location = normalize_text(item.get('location'))
            doctor.address = item.get('address')
            doctor.phone = item.get('phone')
            doctor.email = (item.get('email') or '').strip() or None
            doctor.postal_code = item.get('postal_code')
            doctor.county = item.get('county')
            doctor.years_experience = item.get('years_experience')
            doctor.education = item.get('education')
            doctor.languages = '|'.join(item.get('languages') or [])
            doctor.availability = item.get('availability')
            doctor.rating = item.get('rating')
            doctor.updated_at = datetime.utcnow()

        processed += 1

    db.flush()
    return {'processed': processed, 'rejected': rejected, 'created': created}


def sync_data(db: Session, *, source: str | None = None) -> SyncRun:
    sync_run = SyncRun(started_at=datetime.utcnow(), status='running', total_records_received=0, total_records_processed=0, total_records_rejected=0)
    db.add(sync_run)
    db.flush()

    try:
        records = fetch_upstream_records(source)
        sync_run.total_records_received = len(records)
        metrics = ingest_records(db, records)
        sync_run.total_records_processed = metrics['processed']
        sync_run.total_records_rejected = metrics['rejected']
        sync_run.status = 'success'
        sync_run.finished_at = datetime.utcnow()
        db.commit()
        return sync_run
    except Exception as exc:
        sync_run.status = 'failed'
        sync_run.finished_at = datetime.utcnow()
        sync_run.error_message = str(exc)
        db.commit()
        raise
