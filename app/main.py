from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.clinics import router as clinics_router
from app.api.doctors import router as doctors_router
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.core.database import engine
from app.core.config import get_settings
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.sync_run import SyncRun

settings = get_settings()

app = FastAPI(title=settings.app_name, version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(doctors_router)
app.include_router(clinics_router)
app.include_router(search_router)
app.include_router(admin_router)


@app.get('/')
def root():
    return {'message': settings.app_name}


@app.on_event('startup')
def startup_event() -> None:
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
