# Healthcare Directory Search API

A FastAPI + SQLAlchemy + PostgreSQL template for a healthcare directory search backend using `pg_trgm` and normalized text fields.

## Stack

- Python 3.11+
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2
- Alembic
- Pydantic v2
- `pg_trgm` + `unaccent`
- pytest

## Quick start

1. Create a virtual environment.
2. Install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

3. Create a local PostgreSQL database and set `DATABASE_URL` in `.env`.
4. Run migrations:

```bash
alembic upgrade head
```

5. Import the JSON data:

```bash
python scripts/import_data.py
```

6. Start the API:

```bash
uvicorn app.main:app --reload
```

## Environment

Copy `.env.example` to `.env` and update values.

## Search behavior

- Normalized exact names are stored in `normalized_full_name` and `normalized_speciality`.
- `pg_trgm` indexes support fuzzy matching on normalized text.
- A supplementary `b/v` normalization is used for common transcription issues but applied cautiously.
- Search results are ranked by normalized exact/partial/trigram similarity.

## How to add filters

Extend the repository query and the endpoint parameters. Example:

```python
if speciality:
    conditions.append(Doctor.normalized_speciality.ilike(f'%{normalize_text(speciality)}%'))
```

## Similarity thresholds

Tune values in `app/core/config.py`.

## Modify database models

Update the model classes in `app/models/*.py`, then generate a new Alembic migration.

## Change sync frequency

Modify `SYNC_INTERVAL_HOURS` in `.env` or the environment. A production worker can use cron or APScheduler.

## Connect the real upstream API

Set `UPSTREAM_API_URL` in `.env` or pass it to `sync_data()`.

## Add endpoints

Create a router in `app/api/*.py`, include it in `app/main.py`, and keep business logic in `app/services/*`.

## Manual sync

```bash
curl -X POST http://localhost:8000/admin/sync \
  -H 'X-Admin-Token: change-me'
```

## Test

```bash
pytest -q
```
