"""
Doctor Onboarding — API Endpoints
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dependencies.auth import get_doctor
from models.user import User
from models.doctor import DocumentType
from services.doctor_service import DoctorService
from schemas.doctor import (
    PersonalInfoUpdate,
    PersonalInfoResponse,
    ProfessionalInfoUpdate,
    ProfessionalInfoResponse,
    QualificationCreate,
    QualificationResponse,
    SpecializationsUpdate,
    SpecializationResponse,
    ClinicCreate,
    ClinicUpdate,
    ClinicResponse,
    DocumentResponse,
    VerificationResponse,
    DashboardResponse,
    DoctorFullProfile,
    DoctorPublicProfile,
    ReferenceDataResponse,
    MEDICAL_COUNCILS,
    SPECIALIZATIONS,
    INDIAN_STATES,
)

router = APIRouter(prefix="/doctor", tags=["Doctor Onboarding"])


# ═══════════════════════════════════════════════════════════════════════════════
# Reference Data (public — used by frontend dropdowns)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/reference-data",
    response_model=ReferenceDataResponse,
    summary="Get all dropdown/reference data for doctor onboarding forms",
)
async def get_reference_data():
    return ReferenceDataResponse(
        medical_councils=MEDICAL_COUNCILS,
        specializations=SPECIALIZATIONS,
        qualification_types=[qt.value for qt in DocumentType.__class__.__mro__[0].__members__.values()]
        if False else [
            "MBBS", "BDS", "BHMS", "BAMS", "MD", "MS", "DM", "MCh", "DNB", "OTHER"
        ],
        indian_states=INDIAN_STATES,
        document_types=[dt.value for dt in DocumentType],
        days_of_week=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Full Profile
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/profile",
    response_model=DoctorFullProfile,
    summary="Get complete doctor profile",
)
async def get_profile(
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.get_full_profile(current_user)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1 — Personal Information
# ═══════════════════════════════════════════════════════════════════════════════

@router.put(
    "/profile/personal",
    response_model=PersonalInfoResponse,
    summary="Step 1: Save personal information",
)
async def save_personal_info(
    data: PersonalInfoUpdate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.save_personal_info(current_user, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 — Professional Information
# ═══════════════════════════════════════════════════════════════════════════════

@router.put(
    "/profile/professional",
    response_model=ProfessionalInfoResponse,
    summary="Step 2: Save professional information",
)
async def save_professional_info(
    data: ProfessionalInfoUpdate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.save_professional_info(current_user, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3 — Qualifications
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/profile/qualifications",
    response_model=QualificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Step 3: Add a qualification",
)
async def add_qualification(
    data: QualificationCreate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.add_qualification(current_user, data)


@router.get(
    "/profile/qualifications",
    response_model=List[QualificationResponse],
    summary="Get all qualifications",
)
async def get_qualifications(
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.get_qualifications(current_user)


@router.delete(
    "/profile/qualifications/{qual_id}",
    summary="Remove a qualification",
)
async def delete_qualification(
    qual_id: UUID,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.delete_qualification(current_user, qual_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4 — Specializations
# ═══════════════════════════════════════════════════════════════════════════════

@router.put(
    "/profile/specializations",
    response_model=List[SpecializationResponse],
    summary="Step 4: Set specializations (replaces all)",
)
async def save_specializations(
    data: SpecializationsUpdate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.save_specializations(current_user, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 5 — Practice / Clinics
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/profile/clinics",
    response_model=ClinicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Step 5: Add a clinic with availability",
)
async def create_clinic(
    data: ClinicCreate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.create_clinic(current_user, data)


@router.put(
    "/profile/clinics/{clinic_id}",
    response_model=ClinicResponse,
    summary="Update a clinic",
)
async def update_clinic(
    clinic_id: UUID,
    data: ClinicUpdate,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.update_clinic(current_user, clinic_id, data)


@router.delete(
    "/profile/clinics/{clinic_id}",
    summary="Remove a clinic",
)
async def delete_clinic(
    clinic_id: UUID,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.delete_clinic(current_user, clinic_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Step 6 — Documents
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/profile/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Step 6: Upload a verification document",
)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    try:
        doc_type = DocumentType(document_type)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Must be one of: {[dt.value for dt in DocumentType]}",
        )
    svc = DoctorService(db)
    return await svc.upload_document(current_user, doc_type, file)


@router.post(
    "/profile/photo",
    summary="Upload profile photo",
)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.upload_profile_photo(current_user, file)


@router.delete(
    "/profile/documents/{doc_id}",
    summary="Remove a document",
)
async def delete_document(
    doc_id: UUID,
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.delete_document(current_user, doc_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Verification Submit
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/profile/submit",
    response_model=VerificationResponse,
    summary="Submit profile for verification",
)
async def submit_for_verification(
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.submit_for_verification(current_user)


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get doctor dashboard data",
)
async def get_dashboard(
    current_user: User = Depends(get_doctor),
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.get_dashboard(current_user)


# ═══════════════════════════════════════════════════════════════════════════════
# Public Profile (patient-facing)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/public/{doctor_profile_id}",
    response_model=DoctorPublicProfile,
    summary="Get public doctor profile (for patients)",
)
async def get_public_profile(
    doctor_profile_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = DoctorService(db)
    return await svc.get_public_profile(doctor_profile_id)
