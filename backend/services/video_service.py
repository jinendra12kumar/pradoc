"""
Video Consultation Service — Jitsi Meet Room Management
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.appointment import (
    Appointment, AppointmentStatus, ConsultationType,
    PatientProfile, AppointmentStatusHistory,
)
from models.doctor import DoctorProfile
from models.user import User, UserRole


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Room name — deterministic, no storage needed ──────────────────────────
    @staticmethod
    def _room_name(appointment_id: UUID) -> str:
        return f"pradoc-{str(appointment_id).replace('-', '')}"

    # ── Fetch + access-check appointment ─────────────────────────────────────
    async def _get_appointment(self, appointment_id: UUID) -> Appointment:
        appt = await self.db.get(Appointment, appointment_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found.")
        return appt

    async def _assert_confirmed_online(self, appt: Appointment) -> None:
        if appt.consultation_type != ConsultationType.online:
            raise HTTPException(
                status_code=400,
                detail="Video consultation is only available for online appointments.",
            )
        if appt.status != AppointmentStatus.confirmed:
            raise HTTPException(
                status_code=400,
                detail="Video consultation is only available for confirmed appointments.",
            )

    # ── Doctor: create / start meeting ───────────────────────────────────────
    async def create_meeting(self, appointment_id: UUID, doctor: User) -> dict:
        appt = await self._get_appointment(appointment_id)
        await self._assert_confirmed_online(appt)

        # Verify doctor owns this appointment
        dp_r = await self.db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == doctor.id)
        )
        dp = dp_r.scalar_one_or_none()
        if not dp or dp.id != appt.doctor_profile_id:
            raise HTTPException(status_code=403, detail="Not authorised for this appointment.")

        # Set meeting_started_at if not already
        if not appt.meeting_started_at:
            appt.meeting_started_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(appt)

        return {
            "room_name": self._room_name(appointment_id),
            "display_name": f"Dr. {doctor.full_name}",
            "is_host": True,
            "meeting_started_at": appt.meeting_started_at.isoformat() if appt.meeting_started_at else None,
        }

    # ── Get join info (doctor or patient) ────────────────────────────────────
    async def get_join_info(self, appointment_id: UUID, user: User) -> dict:
        appt = await self._get_appointment(appointment_id)
        await self._assert_confirmed_online(appt)

        is_doctor = user.role == UserRole.doctor
        is_patient = user.role == UserRole.patient

        if is_doctor:
            dp_r = await self.db.execute(
                select(DoctorProfile).where(DoctorProfile.user_id == user.id)
            )
            dp = dp_r.scalar_one_or_none()
            if not dp or dp.id != appt.doctor_profile_id:
                raise HTTPException(status_code=403, detail="Not authorised.")
        elif is_patient:
            pp_r = await self.db.execute(
                select(PatientProfile).where(PatientProfile.user_id == user.id)
            )
            pp = pp_r.scalar_one_or_none()
            if not pp or pp.id != appt.patient_id:
                raise HTTPException(status_code=403, detail="Not authorised.")
        else:
            raise HTTPException(status_code=403, detail="Not authorised.")

        return {
            "room_name": self._room_name(appointment_id),
            "display_name": user.full_name,
            "is_host": is_doctor,
            "meeting_started": appt.meeting_started_at is not None,
            "meeting_started_at": appt.meeting_started_at.isoformat() if appt.meeting_started_at else None,
            "meeting_ended_at": appt.meeting_ended_at.isoformat() if appt.meeting_ended_at else None,
            "appointment_date": str(appt.appointment_date),
            "slot_start_time": str(appt.slot_start_time),
        }

    # ── Doctor: end meeting ───────────────────────────────────────────────────
    async def end_meeting(self, appointment_id: UUID, doctor: User) -> dict:
        appt = await self._get_appointment(appointment_id)

        dp_r = await self.db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == doctor.id)
        )
        dp = dp_r.scalar_one_or_none()
        if not dp or dp.id != appt.doctor_profile_id:
            raise HTTPException(status_code=403, detail="Not authorised.")

        now = datetime.utcnow()
        appt.meeting_ended_at = now
        appt.status = AppointmentStatus.completed
        appt.completed_at = now

        self.db.add(AppointmentStatusHistory(
            appointment_id=appt.id,
            old_status=AppointmentStatus.confirmed.value,
            new_status=AppointmentStatus.completed.value,
            changed_by=doctor.id,
            note="Completed via video consultation.",
        ))
        await self.db.commit()

        return {"message": "Meeting ended. Appointment marked as completed.", "appointment_id": str(appointment_id)}
