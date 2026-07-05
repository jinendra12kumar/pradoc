"""
Appointment Service — Business Logic + Redis Slot Locking
"""
from __future__ import annotations

import json
from datetime import date, time, datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import redis.asyncio as aioredis

from models.appointment import (
    Appointment, AppointmentStatus, AppointmentStatusHistory,
    PatientProfile, Prescription, MedicalRecord, Notification,
    NotificationType, ConsultationType,
)
from models.doctor import DoctorProfile, DoctorClinic, DoctorAvailability, DayOfWeek
from models.user import User
from schemas.appointment import (
    AppointmentCreate, AppointmentStatusUpdate,
    PrescriptionCreate, PatientProfileUpdate,
    MedicalRecordCreate,
)


def _fire_email(task_fn, *args, **kwargs):
    """Fire Celery email task — silently skips if Celery/RabbitMQ is unavailable."""
    try:
        task_fn.delay(*args, **kwargs)
    except Exception:
        pass

SLOT_LOCK_TTL = 300  # 5 minutes


# ─── Helper: day name → DayOfWeek enum ───────────────────────────────────────
_DAY_MAP = {
    "Monday": DayOfWeek.MON, "Tuesday": DayOfWeek.TUE,
    "Wednesday": DayOfWeek.WED, "Thursday": DayOfWeek.THU,
    "Friday": DayOfWeek.FRI, "Saturday": DayOfWeek.SAT,
    "Sunday": DayOfWeek.SUN,
}


def _slot_lock_key(clinic_id: UUID, appt_date: date, start_time: str) -> str:
    return f"slot_lock:{clinic_id}:{appt_date.isoformat()}:{start_time}"


def _generate_slots(start: time, end: time, duration_mins: int = 15) -> List[dict]:
    """Generate time slots between start and end with given duration."""
    slots = []
    current = datetime.combine(date.today(), start)
    end_dt  = datetime.combine(date.today(), end)
    while current + timedelta(minutes=duration_mins) <= end_dt:
        slot_end = current + timedelta(minutes=duration_mins)
        slots.append({
            "start_time": current.time(),
            "end_time":   slot_end.time(),
            "slot_label": current.strftime("%I:%M %p"),
        })
        current = slot_end
    return slots


class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Ensure patient profile exists ─────────────────────────────────────────
    async def _get_or_create_patient_profile(self, user: User) -> PatientProfile:
        result = await self.db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = PatientProfile(user_id=user.id)
            self.db.add(profile)
            await self.db.flush()
        return profile

    # ─────────────────────────────────────────────────────────────────────────
    # SLOT AVAILABILITY
    # ─────────────────────────────────────────────────────────────────────────
    async def get_available_slots(
        self,
        clinic_id: UUID,
        doctor_profile_id: UUID,
        appt_date: date,
        redis: aioredis.Redis,
    ) -> dict:
        day_name = appt_date.strftime("%A")
        day_enum = _DAY_MAP.get(day_name)

        # Fetch availability schedule
        avail_result = await self.db.execute(
            select(DoctorAvailability).where(
                and_(
                    DoctorAvailability.clinic_id == clinic_id,
                    DoctorAvailability.day_of_week == day_enum,
                    DoctorAvailability.is_active == True,
                )
            )
        )
        avail_rows = avail_result.scalars().all()
        if not avail_rows:
            return {"clinic_id": clinic_id, "doctor_profile_id": doctor_profile_id,
                    "date": appt_date, "slots": [], "next_available_slots": []}

        # Fetch already booked slots for that day
        booked_result = await self.db.execute(
            select(Appointment.slot_start_time).where(
                and_(
                    Appointment.clinic_id == clinic_id,
                    Appointment.doctor_profile_id == doctor_profile_id,
                    Appointment.appointment_date == appt_date,
                    Appointment.status.in_([
                        AppointmentStatus.pending,
                        AppointmentStatus.confirmed,
                    ]),
                )
            )
        )
        booked_times = {row for row in booked_result.scalars().all()}

        all_slots = []
        for row in avail_rows:
            dur = getattr(row, "slot_duration_minutes", 15) or 15
            for s in _generate_slots(row.start_time, row.end_time, dur):
                # Check Redis lock too
                lock_key = _slot_lock_key(clinic_id, appt_date, s["start_time"].strftime("%H:%M"))
                locked = await redis.exists(lock_key)
                is_available = (s["start_time"] not in booked_times) and (not locked)
                all_slots.append({**s, "is_available": is_available})

        next_available = [s for s in all_slots if s["is_available"]][:5]
        return {
            "clinic_id": clinic_id,
            "doctor_profile_id": doctor_profile_id,
            "date": appt_date,
            "slots": all_slots,
            "next_available_slots": next_available,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # BOOK APPOINTMENT (with Redis lock)
    # ─────────────────────────────────────────────────────────────────────────
    async def book_appointment(
        self, payload: AppointmentCreate, user: User, redis: aioredis.Redis
    ) -> Appointment:
        patient = await self._get_or_create_patient_profile(user)
        lock_key = _slot_lock_key(
            payload.clinic_id, payload.appointment_date, payload.slot_start_time
        )

        # Acquire Redis slot lock (SETNX)
        acquired = await redis.set(
            lock_key, str(patient.id), nx=True, ex=SLOT_LOCK_TTL
        )
        if not acquired:
            existing_holder = await redis.get(lock_key)
            if existing_holder and existing_holder != str(patient.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This slot is currently being booked by another patient. Please try a different slot.",
                )

        # DB duplicate check
        from datetime import time as dtime
        parts = payload.slot_start_time.split(":")
        st = dtime(int(parts[0]), int(parts[1]))

        existing = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.clinic_id == payload.clinic_id,
                    Appointment.doctor_profile_id == payload.doctor_profile_id,
                    Appointment.appointment_date == payload.appointment_date,
                    Appointment.slot_start_time == st,
                    Appointment.status.in_([
                        AppointmentStatus.pending,
                        AppointmentStatus.confirmed,
                    ]),
                )
            )
        )
        if existing.scalar_one_or_none():
            await redis.delete(lock_key)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This slot is already booked. Please choose another slot.",
            )

        # Fetch clinic fee
        clinic = await self.db.get(DoctorClinic, payload.clinic_id)
        fee = clinic.consultation_fee if clinic else None
        if payload.consultation_type == "online" and clinic and clinic.online_consultation_fee:
            fee = clinic.online_consultation_fee

        # Parse times
        ep = payload.slot_end_time.split(":")
        et = dtime(int(ep[0]), int(ep[1]))

        appt = Appointment(
            patient_id=patient.id,
            doctor_profile_id=payload.doctor_profile_id,
            clinic_id=payload.clinic_id,
            appointment_date=payload.appointment_date,
            slot_start_time=st,
            slot_end_time=et,
            consultation_type=ConsultationType(payload.consultation_type),
            patient_notes=payload.patient_notes,
            status=AppointmentStatus.pending,
            fee_charged=fee,
        )
        self.db.add(appt)
        await self.db.flush()

        # Status history
        history = AppointmentStatusHistory(
            appointment_id=appt.id,
            old_status=None,
            new_status=AppointmentStatus.pending.value,
            changed_by=user.id,
        )
        self.db.add(history)

        # Notify doctor (in-app)
        doctor = await self.db.get(DoctorProfile, payload.doctor_profile_id)
        if doctor:
            self.db.add(Notification(
                user_id=doctor.user_id,
                notification_type=NotificationType.appointment_booked,
                title="New Appointment Booked",
                message=f"{user.full_name} has booked an appointment on {payload.appointment_date} at {payload.slot_start_time}.",
                data={"appointment_id": str(appt.id)},
            ))

        await self.db.commit()
        await self.db.refresh(appt)
        await redis.delete(lock_key)

        # Send email to patient
        from tasks.email_tasks import send_appointment_booked
        _fire_email(
            send_appointment_booked,
            user.email,
            user.full_name,
            doctor.user.full_name if doctor and doctor.user else "Doctor",
            str(payload.appointment_date),
            payload.slot_start_time,
            clinic.clinic_name if clinic else "Clinic",
            str(fee or 0),
            payload.consultation_type,
        )
        return appt

    # ─────────────────────────────────────────────────────────────────────────
    # STATUS TRANSITIONS
    # ─────────────────────────────────────────────────────────────────────────
    async def _change_status(
        self, appt_id: UUID, new_status: AppointmentStatus,
        changed_by: User, note: str | None = None, extra_fields: dict | None = None,
    ) -> Appointment:
        appt = await self.db.get(Appointment, appt_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found.")
        old = appt.status.value
        appt.status = new_status
        if extra_fields:
            for k, v in extra_fields.items():
                setattr(appt, k, v)
        self.db.add(AppointmentStatusHistory(
            appointment_id=appt.id, old_status=old,
            new_status=new_status.value, changed_by=changed_by.id, note=note,
        ))
        await self.db.commit()
        await self.db.refresh(appt)
        return appt

    async def confirm_appointment(self, appt_id: UUID, doctor: User) -> Appointment:
        appt = await self._change_status(
            appt_id, AppointmentStatus.confirmed, doctor,
            extra_fields={"confirmed_at": datetime.utcnow()},
        )
        # Email patient
        from tasks.email_tasks import send_appointment_confirmed
        patient_profile = await self.db.get(PatientProfile, appt.patient_id)
        clinic = await self.db.get(DoctorClinic, appt.clinic_id)
        if patient_profile and patient_profile.user:
            _fire_email(
                send_appointment_confirmed,
                patient_profile.user.email,
                patient_profile.user.full_name,
                doctor.full_name,
                str(appt.appointment_date),
                str(appt.slot_start_time),
                clinic.clinic_name if clinic else "Clinic",
            )
        return appt

    async def complete_appointment(self, appt_id: UUID, doctor: User) -> Appointment:
        return await self._change_status(
            appt_id, AppointmentStatus.completed, doctor,
            extra_fields={"completed_at": datetime.utcnow()},
        )

    async def cancel_appointment(self, appt_id: UUID, user: User, reason: str | None) -> Appointment:
        appt = await self._change_status(
            appt_id, AppointmentStatus.cancelled, user, note=reason,
            extra_fields={"cancelled_at": datetime.utcnow(), "cancellation_reason": reason},
        )
        # Email patient
        from tasks.email_tasks import send_appointment_cancelled
        patient_profile = await self.db.get(PatientProfile, appt.patient_id)
        doctor_profile  = await self.db.get(DoctorProfile, appt.doctor_profile_id)
        if patient_profile and patient_profile.user:
            _fire_email(
                send_appointment_cancelled,
                patient_profile.user.email,
                patient_profile.user.full_name,
                doctor_profile.user.full_name if doctor_profile and doctor_profile.user else "Doctor",
                str(appt.appointment_date),
                str(appt.slot_start_time),
                reason,
            )
        return appt

    async def mark_no_show(self, appt_id: UUID, doctor: User) -> Appointment:
        return await self._change_status(appt_id, AppointmentStatus.no_show, doctor)

    # ─────────────────────────────────────────────────────────────────────────
    # PATIENT QUERIES
    # ─────────────────────────────────────────────────────────────────────────
    async def get_patient_appointments(
        self, user: User, status_filter: str | None, page: int, page_size: int
    ) -> dict:
        patient = await self._get_or_create_patient_profile(user)
        q = select(Appointment).where(Appointment.patient_id == patient.id)
        if status_filter:
            q = q.where(Appointment.status == AppointmentStatus(status_filter))
        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        total = total_r.scalar()
        items_r = await self.db.execute(q.order_by(Appointment.appointment_date.desc()).offset((page-1)*page_size).limit(page_size))
        return {"total": total, "page": page, "page_size": page_size, "items": items_r.scalars().all()}

    async def get_patient_dashboard(self, user: User) -> dict:
        patient = await self._get_or_create_patient_profile(user)
        today = date.today()
        upcoming = await self.db.execute(
            select(Appointment).where(
                and_(Appointment.patient_id == patient.id,
                     Appointment.appointment_date >= today,
                     Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]))
            ).order_by(Appointment.appointment_date).limit(5)
        )
        past = await self.db.execute(
            select(func.count()).where(
                and_(Appointment.patient_id == patient.id,
                     Appointment.appointment_date < today)
            )
        )
        cancelled = await self.db.execute(
            select(func.count()).where(
                and_(Appointment.patient_id == patient.id,
                     Appointment.status == AppointmentStatus.cancelled)
            )
        )
        unread = await self.db.execute(
            select(func.count()).where(
                and_(Notification.user_id == user.id, Notification.is_read == False)
            )
        )
        rx_r = await self.db.execute(
            select(Prescription).where(Prescription.patient_id == patient.id)
            .order_by(Prescription.created_at.desc()).limit(3)
        )
        return {
            "upcoming_count": len(upcoming.scalars().all()),
            "past_count": past.scalar() or 0,
            "cancelled_count": cancelled.scalar() or 0,
            "unread_notifications": unread.scalar() or 0,
            "upcoming_appointments": upcoming.scalars().all(),
            "recent_prescriptions": rx_r.scalars().all(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # DOCTOR QUERIES
    # ─────────────────────────────────────────────────────────────────────────
    async def get_doctor_appointments(
        self, doctor_profile_id: UUID, status_filter: str | None,
        date_filter: str | None, page: int, page_size: int
    ) -> dict:
        q = select(Appointment).where(Appointment.doctor_profile_id == doctor_profile_id)
        if status_filter:
            q = q.where(Appointment.status == AppointmentStatus(status_filter))
        if date_filter == "today":
            q = q.where(Appointment.appointment_date == date.today())
        elif date_filter == "upcoming":
            q = q.where(Appointment.appointment_date >= date.today())
        elif date_filter == "past":
            q = q.where(Appointment.appointment_date < date.today())
        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(q.order_by(Appointment.appointment_date, Appointment.slot_start_time).offset((page-1)*page_size).limit(page_size))
        return {"total": total_r.scalar(), "page": page, "page_size": page_size, "items": items_r.scalars().all()}

    async def get_doctor_dashboard(self, doctor_profile_id: UUID) -> dict:
        today = date.today()
        today_r = await self.db.execute(
            select(Appointment).where(
                and_(Appointment.doctor_profile_id == doctor_profile_id,
                     Appointment.appointment_date == today)
            ).order_by(Appointment.slot_start_time)
        )
        upcoming_c = await self.db.execute(
            select(func.count()).where(
                and_(Appointment.doctor_profile_id == doctor_profile_id,
                     Appointment.appointment_date > today,
                     Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]))
            )
        )
        completed_c = await self.db.execute(
            select(func.count()).where(
                and_(Appointment.doctor_profile_id == doctor_profile_id,
                     Appointment.status == AppointmentStatus.completed)
            )
        )
        pending_c = await self.db.execute(
            select(func.count()).where(
                and_(Appointment.doctor_profile_id == doctor_profile_id,
                     Appointment.status == AppointmentStatus.pending)
            )
        )
        return {
            "today_count": len(today_r.scalars().all()),
            "upcoming_count": upcoming_c.scalar() or 0,
            "completed_count": completed_c.scalar() or 0,
            "pending_count": pending_c.scalar() or 0,
            "today_appointments": today_r.scalars().all(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # PRESCRIPTION
    # ─────────────────────────────────────────────────────────────────────────
    async def create_prescription(self, payload: PrescriptionCreate, doctor: User) -> Prescription:
        doctor_profile = await self.db.execute(
            select(DoctorProfile).where(DoctorProfile.user_id == doctor.id)
        )
        dp = doctor_profile.scalar_one_or_none()
        if not dp:
            raise HTTPException(status_code=404, detail="Doctor profile not found.")

        appt = await self.db.get(Appointment, payload.appointment_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found.")

        existing = await self.db.execute(
            select(Prescription).where(Prescription.appointment_id == payload.appointment_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Prescription already exists for this appointment.")

        rx = Prescription(
            appointment_id=payload.appointment_id,
            doctor_profile_id=dp.id,
            patient_id=appt.patient_id,
            diagnosis=payload.diagnosis,
            medicines=[m.model_dump() for m in payload.medicines],
            instructions=payload.instructions,
            follow_up_date=payload.follow_up_date,
        )
        self.db.add(rx)

        # In-app notification
        patient = await self.db.get(PatientProfile, appt.patient_id)
        if patient:
            self.db.add(Notification(
                user_id=patient.user_id,
                notification_type=NotificationType.prescription_ready,
                title="Prescription Ready 💊",
                message=f"Dr. {doctor.full_name} has created a prescription for your appointment on {appt.appointment_date}.",
                data={"appointment_id": str(appt.id), "prescription_id": str(rx.id)},
            ))

        await self.db.commit()
        await self.db.refresh(rx)

        # Email patient
        from tasks.email_tasks import send_prescription_ready
        if patient and patient.user:
            _fire_email(
                send_prescription_ready,
                patient.user.email,
                patient.user.full_name,
                doctor.full_name,
                payload.diagnosis,
                [m.model_dump() for m in payload.medicines],
                str(payload.follow_up_date) if payload.follow_up_date else None,
            )
        return rx

    async def get_patient_prescriptions(self, user: User) -> list:
        patient = await self._get_or_create_patient_profile(user)
        r = await self.db.execute(
            select(Prescription).where(Prescription.patient_id == patient.id)
            .order_by(Prescription.created_at.desc())
        )
        return r.scalars().all()

    # ─────────────────────────────────────────────────────────────────────────
    # NOTIFICATIONS
    # ─────────────────────────────────────────────────────────────────────────
    async def get_notifications(self, user: User, unread_only: bool = False) -> list:
        q = select(Notification).where(Notification.user_id == user.id)
        if unread_only:
            q = q.where(Notification.is_read == False)
        r = await self.db.execute(q.order_by(Notification.created_at.desc()).limit(50))
        return r.scalars().all()

    async def mark_notification_read(self, notif_id: UUID, user: User) -> None:
        n = await self.db.get(Notification, notif_id)
        if n and n.user_id == user.id:
            n.is_read = True
            await self.db.commit()

    # ─────────────────────────────────────────────────────────────────────────
    # PATIENT PROFILE
    # ─────────────────────────────────────────────────────────────────────────
    async def get_patient_profile(self, user: User) -> PatientProfile:
        return await self._get_or_create_patient_profile(user)

    async def update_patient_profile(self, user: User, payload: PatientProfileUpdate) -> PatientProfile:
        profile = await self._get_or_create_patient_profile(user)
        for field, val in payload.model_dump(exclude_none=True).items():
            setattr(profile, field, val)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    # ─────────────────────────────────────────────────────────────────────────
    # MEDICAL RECORDS
    # ─────────────────────────────────────────────────────────────────────────
    async def get_medical_records(self, user: User) -> list:
        patient = await self._get_or_create_patient_profile(user)
        r = await self.db.execute(
            select(MedicalRecord).where(MedicalRecord.patient_id == patient.id)
            .order_by(MedicalRecord.created_at.desc())
        )
        return r.scalars().all()

    async def create_medical_record(self, user: User, payload: MedicalRecordCreate) -> MedicalRecord:
        patient = await self._get_or_create_patient_profile(user)
        rec = MedicalRecord(
            patient_id=patient.id,
            uploaded_by=user.id,
            **payload.model_dump(),
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    # ─────────────────────────────────────────────────────────────────────────
    # DOCTOR — PATIENT VIEW
    # ─────────────────────────────────────────────────────────────────────────
    async def get_patient_history_for_doctor(
        self, patient_profile_id: UUID, doctor_profile_id: UUID
    ) -> dict:
        appts_r = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.patient_id == patient_profile_id,
                    Appointment.doctor_profile_id == doctor_profile_id,
                )
            ).order_by(Appointment.appointment_date.desc())
        )
        prescriptions_r = await self.db.execute(
            select(Prescription).where(
                and_(
                    Prescription.patient_id == patient_profile_id,
                    Prescription.doctor_profile_id == doctor_profile_id,
                )
            ).order_by(Prescription.created_at.desc())
        )
        return {
            "appointments": appts_r.scalars().all(),
            "prescriptions": prescriptions_r.scalars().all(),
        }
