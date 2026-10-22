import json
from pathlib import Path

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.ingestion import sync_data


def main() -> None:
    settings = get_settings()
    source = Path('/Users/hugosegoviano/Desktop/Proyecto FastAPI/healthcare_data (1).json')
    db = SessionLocal()
    try:
        result = sync_data(db, source=str(source))
        print({'status': result.status, 'received': result.total_records_received, 'processed': result.total_records_processed, 'rejected': result.total_records_rejected})
    finally:
        db.close()


if __name__ == '__main__':
    main()
