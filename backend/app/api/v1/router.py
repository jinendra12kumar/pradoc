from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.doctor import router as doctor_router
from app.api.v1.patient import router as patient_router
from app.api.v1.appointments import router as appointments_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.file_endpoints import router as files_router
from app.api.v1.video import router as video_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(doctor_router)
api_router.include_router(patient_router)
api_router.include_router(appointments_router)
api_router.include_router(reviews_router)
api_router.include_router(files_router)
api_router.include_router(video_router)
api_router.include_router(admin_router)


