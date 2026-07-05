"""
Appointment System — Pydantic v2 Schemas
"""
from __future__ import annotations

import enum
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# Slot Mode Enum (two booking modes)
# ═══════════════════════════════════════════════════════════════════════════════

class SlotSelectionMode(str, enum.Enum):
    pick_time   = "pick_time"    # Patient picks a specific time from grid
    next_available = "next_available"  # Show auto-suggested next free slots


# ═══════════════════════════════════════════════════════════════════════════════
# Slot / Availability
# ═══════════════════════════════════════════════════════════════════════════════

class SlotItem(BaseModel):
    start_time: time
    end_time: time
    is_available: bool
    slot_label: str   # e.g. "10:00 AM"


class SlotAvailabilityRequest(BaseModel):
    clinic_id: UUID
    doctor_profile_id: UUID
    date: date


class SlotAvailabilityResponse(BaseModel):
    clinic_id: UUID
    doctor_profile_id: UUID
    date: date
    slots: List[SlotItem]
    next_available_slots: List[SlotItem]   # Pre-filtered list of free slots


# ═══════════════════════════════════════════════════════════════════════════════
# Booking
# ═══════════════════════════════════════════════════════════════════════════════

class AppointmentCreate(BaseModel):
    doctor_profile_id: UUID
    clinic_id: UUID
    appointment_date: date
    slot_start_time: str     # "10:00"
    slot_end_time: str       # "10:15"
    consultation_type: str = "in_clinic"
    patient_notes: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None
    cancellation_reason: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Clinic Info (for booking wizard)
# ═══════════════════════════════════════════════════════════════════════════════

class ClinicInfo(BaseModel):
    id: UUID
    clinic_name: str
    address: str
    city: str
    state: str
    consultation_fee: Decimal
    online_consultation: bool
    online_consultation_fee: Optional[Decimal]
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Appointment Response
# ═══════════════════════════════════════════════════════════════════════════════

class DoctorBrief(BaseModel):
    doctor_profile_id: UUID
    full_name: str
    primary_specialization: Optional[str]
    profile_photo: Optional[str]
    model_config = {"from_attributes": True}


class PatientBrief(BaseModel):
    patient_id: UUID
    full_name: str
    mobile: str
    email: str
    model_config = {"from_attributes": True}


class MedicineItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    notes: Optional[str] = None


class PrescriptionResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    diagnosis: str
    medicines: List[MedicineItem]
    instructions: Optional[str]
    follow_up_date: Optional[date]
    created_at: datetime
    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    id: UUID
    appointment_date: date
    slot_start_time: time
    slot_end_time: time
    consultation_type: str
    status: str
    patient_notes: Optional[str]
    doctor_notes: Optional[str]
    cancellation_reason: Optional[str]
    fee_charged: Optional[Decimal]
    booked_at: datetime
    confirmed_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]

    # Nested
    doctor: Optional[DoctorBrief] = None
    patient: Optional[PatientBrief] = None
    clinic: Optional[ClinicInfo] = None
    prescription: Optional[PrescriptionResponse] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Prescription
# ═══════════════════════════════════════════════════════════════════════════════

class PrescriptionCreate(BaseModel):
    appointment_id: UUID
    diagnosis: str
    medicines: List[MedicineItem]
    instructions: Optional[str] = None
    follow_up_date: Optional[date] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Medical Records
# ═══════════════════════════════════════════════════════════════════════════════

class MedicalRecordCreate(BaseModel):
    title: str
    record_type: str = "other"
    description: Optional[str] = None
    record_date: Optional[date] = None


class MedicalRecordResponse(BaseModel):
    id: UUID
    title: str
    record_type: str
    description: Optional[str]
    record_date: Optional[date]
    created_at: datetime
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Notifications
# ═══════════════════════════════════════════════════════════════════════════════

class NotificationResponse(BaseModel):
    id: UUID
    notification_type: str
    title: str
    message: str
    data: Optional[Any]
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Patient Profile
# ═══════════════════════════════════════════════════════════════════════════════

class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None


class PatientProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    date_of_birth: Optional[date]
    gender: Optional[str]
    blood_group: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    full_name: str
    email: str
    mobile: str
    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard Summaries
# ═══════════════════════════════════════════════════════════════════════════════

class PatientDashboardSummary(BaseModel):
    upcoming_count: int
    past_count: int
    cancelled_count: int
    unread_notifications: int
    upcoming_appointments: List[AppointmentResponse]
    recent_prescriptions: List[PrescriptionResponse]


class DoctorDashboardSummary(BaseModel):
    today_count: int
    upcoming_count: int
    completed_count: int
    pending_count: int
    today_appointments: List[AppointmentResponse]


# ═══════════════════════════════════════════════════════════════════════════════
# Paginated Response
# ═══════════════════════════════════════════════════════════════════════════════

class PaginatedAppointments(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AppointmentResponse]
