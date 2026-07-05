"""
Prescriptions & Medical Records — File endpoints
Prescription PDF download + Medical record file upload
"""
from __future__ import annotations

from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from dependencies.auth import get_patient, get_doctor, get_current_user
from models.user import User
from models.appointment import (
    Prescription, PatientProfile, MedicalRecord, MedicalRecordType,
)
from models.doctor import DoctorProfile, DoctorClinic
from services.file_service import FileService
from services.prescription_pdf import generate_prescription_pdf
from tasks.email_tasks import send_record_uploaded

router = APIRouter(prefix="/files", tags=["Files"])


# ═══════════════════════════════════════════════════════════════════════════════
# PRESCRIPTION DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/prescription/{prescription_id}/download",
    summary="Download prescription as PDF (or HTML fallback)",
)
async def download_prescription(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch prescription
    rx = await db.get(Prescription, prescription_id)
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found.")

    # Access check: must be the patient or the doctor
    patient_profile = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == current_user.id)
    )
    patient = patient_profile.scalar_one_or_none()

    doctor_profile = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == current_user.id)
    )
    doctor = doctor_profile.scalar_one_or_none()

    is_patient = patient and rx.patient_id == patient.id
    is_doctor  = doctor  and rx.doctor_profile_id == doctor.id

    if not (is_patient or is_doctor):
        raise HTTPException(status_code=403, detail="Access denied.")

    # Gather data
    doc_profile = await db.get(DoctorProfile, rx.doctor_profile_id)
    doc_user    = doc_profile.user if doc_profile else None
    pat_profile = await db.get(PatientProfile, rx.patient_id)
    pat_user    = pat_profile.user if pat_profile else None

    # Get clinic name from the appointment
    from models.appointment import Appointment
    appt     = await db.get(Appointment, rx.appointment_id)
    clinic_r = await db.get(DoctorClinic, appt.clinic_id) if appt else None

    from services.prescription_pdf import REPORTLAB_AVAILABLE
    pdf_bytes = generate_prescription_pdf(
        prescription_id      = str(rx.id),
        doctor_name          = doc_user.full_name if doc_user else "Doctor",
        doctor_specialization= doc_profile.primary_specialization or "" if doc_profile else "",
        clinic_name          = clinic_r.clinic_name if clinic_r else "PraDoc Clinic",
        patient_name         = pat_user.full_name if pat_user else "Patient",
        patient_dob          = str(pat_profile.date_of_birth) if pat_profile and pat_profile.date_of_birth else None,
        diagnosis            = rx.diagnosis,
        medicines            = rx.medicines or [],
        instructions         = rx.instructions,
        follow_up_date       = str(rx.follow_up_date) if rx.follow_up_date else None,
        created_at           = rx.created_at.strftime("%d %b %Y") if rx.created_at else "",
    )

    content_type = "application/pdf" if REPORTLAB_AVAILABLE else "text/html"
    extension    = "pdf"              if REPORTLAB_AVAILABLE else "html"
    filename     = f"prescription_{str(rx.id)[:8]}.{extension}"

    return Response(
        content     = pdf_bytes,
        media_type  = content_type,
        headers     = {"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MEDICAL RECORD FILE UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/medical-records/upload",
    summary="Upload a medical record file (PDF, JPG, PNG — max 5MB)",
)
async def upload_medical_record(
    title:       str = Form(...),
    record_type: str = Form("other"),
    description: str = Form(""),
    record_date: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    # Get or create patient profile
    pat_r = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == current_user.id)
    )
    patient = pat_r.scalar_one_or_none()
    if not patient:
        patient = PatientProfile(user_id=current_user.id)
        db.add(patient)
        await db.flush()

    # Save file
    fs      = FileService()
    rel_path, file_hash, file_size = await fs.save_upload(
        file, str(current_user.id), subfolder="medical_records"
    )

    # Parse record_date
    parsed_date = None
    if record_date:
        try:
            parsed_date = date.fromisoformat(record_date)
        except ValueError:
            pass

    # Validate record_type
    try:
        rt = MedicalRecordType(record_type)
    except ValueError:
        rt = MedicalRecordType.other

    # Save to DB
    record = MedicalRecord(
        patient_id  = patient.id,
        uploaded_by = current_user.id,
        title       = title,
        record_type = rt,
        description = description or None,
        file_path   = rel_path,
        record_date = parsed_date,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    # Fire email notification (async via Celery)
    try:
        send_record_uploaded.delay(
            email        = current_user.email,
            patient_name = current_user.full_name,
            record_title = title,
            record_type  = record_type,
        )
    except Exception:
        pass  # Don't fail the upload if Celery is down

    return {
        "message":   "Record uploaded successfully.",
        "record_id": str(record.id),
        "file_path": rel_path,
        "file_size": file_size,
    }


@router.get(
    "/medical-records/{record_id}/view",
    summary="View / download a medical record file",
)
async def view_medical_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    pat_r = await db.execute(
        select(PatientProfile).where(PatientProfile.user_id == current_user.id)
    )
    patient = pat_r.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    record = await db.get(MedicalRecord, record_id)
    if not record or record.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Record not found.")

    if not record.file_path:
        raise HTTPException(status_code=404, detail="No file attached to this record.")

    fs        = FileService()
    full_path = fs.get_full_path(record.file_path)

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(
        path     = str(full_path),
        filename = f"{record.title.replace(' ','_')}{full_path.suffix}",
        media_type = "application/octet-stream",
    )
