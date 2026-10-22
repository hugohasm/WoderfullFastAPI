from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sync_run import SyncRun

router = APIRouter(tags=['health'])


@router.get('/health')
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False

    last_success = db.query(SyncRun).filter(SyncRun.status == 'success').order_by(SyncRun.finished_at.desc().nullslast()).first()
    return {
        'status': 'ok' if db_ok else 'degraded',
        'database': 'connected' if db_ok else 'disconnected',
        'last_successful_sync': last_success.finished_at.isoformat() if last_success and last_success.finished_at else None,
        'timestamp': datetime.utcnow().isoformat(),
    }
