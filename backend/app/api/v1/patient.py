"""
Patient Portal — API Endpoints for Doctor Discovery
"""
from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.doctor_service import DoctorService
from schemas.doctor import (
    DoctorSearchQuery,
    DoctorSearchResponse,
    PatientHomeData,
    DoctorDetailResponse,
)

router = APIRouter(prefix="/patient", tags=["Patient Portal"])


# ═══════════════════════════════════════════════════════════════════════════════
# Homepage Data
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/home",
    response_model=PatientHomeData,
    summary="Get patient homepage data (specializations, featured doctors, top clinics)",
)
async def get_home_data(db: AsyncSession = Depends(get_db)):
    svc = DoctorService(db)
    return await svc.get_patient_home_data()


# ═══════════════════════════════════════════════════════════════════════════════
# Doctor Search
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/doctors/search",
    response_model=DoctorSearchResponse,
    summary="Search and filter verified doctors",
)
async def search_doctors(
    q: Optional[str] = Query(None, description="Text search (name, specialization)"),
    specialization: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None, ge=0),
    max_experience: Optional[int] = Query(None, ge=0),
    min_fee: Optional[int] = Query(None, ge=0),
    max_fee: Optional[int] = Query(None, ge=0),
    gender: Optional[str] = Query(None),
    online_consultation: Optional[bool] = Query(None),
    city: Optional[str] = Query(None),
    availability_day: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("experience", regex="^(experience|fee|name)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    query = DoctorSearchQuery(
        q=q,
        specialization=specialization,
        min_experience=min_experience,
        max_experience=max_experience,
        min_fee=min_fee,
        max_fee=max_fee,
        gender=gender,
        online_consultation=online_consultation,
        city=city,
        availability_day=availability_day,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    svc = DoctorService(db)
    return await svc.search_doctors(query)


# ═══════════════════════════════════════════════════════════════════════════════
# Doctor Detail
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/doctors/{doctor_profile_id}",
    response_model=DoctorDetailResponse,
    summary="Get full doctor profile for patient view",
)
async def get_doctor_detail(
    doctor_profile_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.get_doctor_detail(doctor_profile_id)
