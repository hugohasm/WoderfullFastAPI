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

## Pipeline and sync cadence

The ingestion pipeline is intentionally simple but clear:

1. `scripts/import_data.py` loads the source payload from the local file or from an upstream endpoint.
2. `app/services/ingestion.py::fetch_upstream_records()` retrieves the records.
3. `ingest_records()` reviews each item and rejects invalid entries.
4. For each valid doctor, it resolves or creates the associated clinic.
5. A deterministic `source_record_key` is built, and the doctor is inserted or updated with an UPSERT-like logic via SQLAlchemy.
6. `sync_data()` creates a `SyncRun` record with timestamps and counters, and stores the result of the synchronization in PostgreSQL.

The cadence of `12` hours is configured through `SYNC_INTERVAL_HOURS` in `.env` and `app/core/config.py`. The reason for that value is operational: the dataset is a directory of healthcare records, so it is not a real-time stream and does not need sub-minute freshness. A 12-hour interval is a reasonable balance between freshness, data quality, and infrastructure cost. In a production deployment, that would usually be enforced with a cron job, APScheduler, or a containerized worker process; in this project, the value is prepared and documented, but the scheduler itself is not yet implemented as the full background worker.

## Data storage and update model in PostgreSQL

The database schema is managed through Alembic and defined in `alembic/versions/20261021_initial.py`.

The important tables are:

- `clinics`: stores the clinic name, location, and sanitized normalized fields.
- `doctors`: stores doctor identity, clinic relation, specialty, location, and profile attributes.
- `sync_runs`: stores execution metadata for each ingestion cycle.

The update logic is intentionally idempotent:

- clinics are searched by `name + location` before being created or updated.
- doctors are matched by `source_record_key`.
- if a doctor already exists, the record is updated in place; otherwise it is created.
- `created_at` and `updated_at` timestamps are maintained for auditing and change tracking.

This pattern is important because it prevents duplicate records and allows the system to reconcile changes from the upstream data source without rebuilding the full table.

## `pg_trgm`, indexes and similarity thresholds

The important database extension is `pg_trgm`, enabled with:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

This allows PostgreSQL to perform trigram-based fuzzy matching on normalized strings. In practice, the data is normalized through `normalize_text()` before being stored, which removes accents, converts to a consistent format, and reduces false mismatches caused by spelling and formatting variation.

The DB migration creates GIN indexes for the normalized text fields:

- `idx_clinics_name_trgm`
- `idx_clinics_location_trgm`
- `idx_doctors_name_trgm`
- `idx_doctors_speciality_trgm`
- `idx_doctors_location_trgm`

These are created with `postgresql_using='gin'` and `postgresql_ops={'field': 'gin_trgm_ops'}` so that trigram search is fast enough for approximate match queries.

The search flow uses:

- `Doctor.normalized_full_name % q_norm`
- `func.similarity(Doctor.normalized_full_name, q_norm)`
- `func.word_similarity(...)`

That lets the API handle small typos, transpositions, and near matches without scanning the entire table linearly.

The similarity thresholds are defined in `app/core/config.py` as:

- `similarity_threshold = 0.2`
- `ambiguity_threshold = 0.05`

In the current implementation, the logic is straightforward and conservative:

- exact normalized equality => score 1.0
- substring inclusion => score 0.9
- otherwise the score falls back to trigram-based similarity logic

So the intended design is: exact > partial > fuzzy similarity; in practice this is a pragmatic approximation that is easy to explain and tune, but it is not yet a fully production-grade ranking model with a strict global threshold enforcement in the query layer.

## Why the deployment was not completed in the interview

This is important to be transparent about: the project is a working local prototype, but it was not a complete production deployment at the time of the interview.

What was already in place:

- local FastAPI project structure
- PostgreSQL schema with Alembic migration
- ingestion pipeline and normalization logic
- search endpoints with fuzzy matching
- Docker and Compose setup for local development

What was still missing for a full deployment:

1. A real scheduler for the 12-hour sync loop.
   - There is configuration, but no actual cron/APScheduler worker running in production.

2. A real cloud deployment target.
   - There was no provisioned database in a managed environment and no deployment pipeline for Azure/App Service/Container Apps/VMs.

3. Environment variables and secrets for production.
   - The project expects `.env` values and service endpoints, but the interview environment did not include a managed external database and production credentials.

4. Runtime validation in a hosted environment.
   - The application was tested locally, but it had not been deployed and smoke-tested in a live infrastructure environment.

5. A full migration from local data ingestion into a production scheduler/worker pattern.
   - The ingestion route is available manually through `/admin/sync`, but automatic scheduled execution was not yet wired into a production runtime.

In other words, the project demonstrated the architecture and the technical decisions correctly, but it was not complete as a production-ready deployment artifact. That is a fair and honest statement, and it is much stronger than pretending the deployment was already finished.

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

## Current status

This project is best described as a solid local prototype with a good architecture for ingestion, normalization, persistence, and fuzzy search. The core engineering decisions are in place, and the repo is organized to support a real production deployment, but the final production automation and hosting layer still need to be implemented before it can be considered fully deployed.
