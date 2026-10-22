from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.services.ingestion import sync_data

router = APIRouter(prefix='/admin', tags=['admin'])
settings = get_settings()


@router.post('/sync')
def manual_sync(
    x_admin_token: str | None = Header(default=None, alias='X-Admin-Token'),
    db: Session = Depends(get_db),
):
    if x_admin_token != settings.admin_api_token:
        raise HTTPException(status_code=401, detail='Unauthorized')
    try:
        sync_run = sync_data(db)
        return {'status': 'success', 'sync_run_id': sync_run.id, 'status_value': sync_run.status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
