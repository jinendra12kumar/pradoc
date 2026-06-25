from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.doctor import router as doctor_router
from app.api.v1.patient import router as patient_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(doctor_router)
api_router.include_router(patient_router)

