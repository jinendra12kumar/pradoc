"""
Appointments — API Router (Patient + Doctor endpoints)
"""
from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.redis_client import get_redis
from dependencies.auth import get_current_user, get_patient, get_doctor
from models.user import User, UserRole
from models.doctor import DoctorProfile
from services.appointment_service import AppointmentService
from schemas.appointment import (
    AppointmentCreate, AppointmentStatusUpdate,
    PrescriptionCreate, PatientProfileUpdate, MedicalRecordCreate,
)
from sqlalchemy import select

router = APIRouter(prefix="/appointments", tags=["Appointments"])


# ═══════════════════════════════════════════════════════════════════════════════
# SLOT AVAILABILITY (public-ish — no auth required)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/slots", summary="Get available time slots for a doctor at a clinic on a date")
async def get_slots(
    clinic_id: UUID = Query(...),
    doctor_profile_id: UUID = Query(...),
    date: str = Query(..., description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    from datetime import date as ddate
    try:
        appt_date = ddate.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    svc = AppointmentService(db)
    return await svc.get_available_slots(clinic_id, doctor_profile_id, appt_date, redis)


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/book", summary="Book an appointment (patient)")
async def book_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    appt = await svc.book_appointment(payload, current_user, redis)
    return {"message": "Appointment booked successfully.", "appointment_id": str(appt.id)}


@router.get("/my", summary="Get patient's appointments")
async def my_appointments(
    status: Optional[str] = Query(None, description="pending|confirmed|completed|cancelled|no_show"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    return await svc.get_patient_appointments(current_user, status, page, page_size)


@router.get("/dashboard/patient", summary="Patient dashboard summary")
async def patient_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    return await svc.get_patient_dashboard(current_user)


@router.put("/{appointment_id}/cancel", summary="Patient cancels appointment")
async def cancel_appointment(
    appointment_id: UUID,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    appt = await svc.cancel_appointment(appointment_id, current_user, reason)
    return {"message": "Appointment cancelled.", "appointment_id": str(appt.id)}


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications", summary="Get notifications for logged-in user")
async def get_notifications(
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = AppointmentService(db)
    return await svc.get_notifications(current_user, unread_only)


@router.put("/notifications/{notif_id}/read", summary="Mark notification as read")
async def mark_notification_read(
    notif_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = AppointmentService(db)
    await svc.mark_notification_read(notif_id, current_user)
    return {"message": "Marked as read."}


# ═══════════════════════════════════════════════════════════════════════════════
# DOCTOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_doctor_profile_id(db: AsyncSession, user: User) -> UUID:
    r = await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == user.id))
    dp = r.scalar_one_or_none()
    if not dp:
        raise HTTPException(status_code=404, detail="Doctor profile not found.")
    return dp.id


@router.get("/dashboard/doctor", summary="Doctor dashboard summary")
async def doctor_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    dp_id = await _get_doctor_profile_id(db, current_user)
    return await svc.get_doctor_dashboard(dp_id)


@router.get("/doctor/list", summary="Doctor's appointment list with filters")
async def doctor_appointments_list(
    status: Optional[str] = Query(None),
    date_filter: Optional[str] = Query(None, description="today|upcoming|past"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    dp_id = await _get_doctor_profile_id(db, current_user)
    return await svc.get_doctor_appointments(dp_id, status, date_filter, page, page_size)


@router.put("/{appointment_id}/confirm", summary="Doctor confirms appointment")
async def confirm_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    appt = await svc.confirm_appointment(appointment_id, current_user)
    return {"message": "Appointment confirmed.", "appointment_id": str(appt.id)}


@router.put("/{appointment_id}/complete", summary="Doctor marks appointment as completed")
async def complete_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    appt = await svc.complete_appointment(appointment_id, current_user)
    return {"message": "Appointment completed.", "appointment_id": str(appt.id)}


@router.put("/{appointment_id}/no-show", summary="Doctor marks patient as no-show")
async def no_show(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    appt = await svc.mark_no_show(appointment_id, current_user)
    return {"message": "Marked as no-show.", "appointment_id": str(appt.id)}


@router.post("/prescription", summary="Create prescription for an appointment")
async def create_prescription(
    payload: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    rx = await svc.create_prescription(payload, current_user)
    return {"message": "Prescription created.", "prescription_id": str(rx.id)}


@router.get("/patients/{patient_profile_id}/history", summary="Doctor views patient history")
async def patient_history_for_doctor(
    patient_profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    svc = AppointmentService(db)
    dp_id = await _get_doctor_profile_id(db, current_user)
    return await svc.get_patient_history_for_doctor(patient_profile_id, dp_id)


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENT PROFILE & RECORDS (under /appointments prefix for routing simplicity)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/profile/me", summary="Get patient profile")
async def get_patient_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    profile = await svc.get_patient_profile(current_user)
    return {
        **{c.name: getattr(profile, c.name) for c in profile.__table__.columns},
        "full_name": current_user.full_name,
        "email": current_user.email,
        "mobile": current_user.mobile,
    }


@router.put("/profile/me", summary="Update patient profile")
async def update_patient_profile(
    payload: PatientProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    profile = await svc.update_patient_profile(current_user, payload)
    return {"message": "Profile updated.", "profile_id": str(profile.id)}


@router.get("/medical-records", summary="Get patient medical records")
async def get_medical_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    return await svc.get_medical_records(current_user)


@router.post("/medical-records", summary="Add a medical record")
async def add_medical_record(
    payload: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    rec = await svc.create_medical_record(current_user, payload)
    return {"message": "Record added.", "record_id": str(rec.id)}


@router.get("/prescriptions/my", summary="Get patient's prescriptions")
async def get_my_prescriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = AppointmentService(db)
    return await svc.get_patient_prescriptions(current_user)
