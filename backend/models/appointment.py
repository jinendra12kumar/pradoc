"""
Appointment Booking & Patient Management — SQLAlchemy Models
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Time, Text, Integer, Numeric,
    Enum as SAEnum, ForeignKey, JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════

class AppointmentStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show   = "no_show"


class ConsultationType(str, enum.Enum):
    in_clinic = "in_clinic"
    online    = "online"


class BloodGroup(str, enum.Enum):
    A_POS  = "A+"
    A_NEG  = "A-"
    B_POS  = "B+"
    B_NEG  = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS  = "O+"
    O_NEG  = "O-"


class NotificationType(str, enum.Enum):
    appointment_booked    = "appointment_booked"
    appointment_confirmed = "appointment_confirmed"
    appointment_cancelled = "appointment_cancelled"
    appointment_reminder  = "appointment_reminder"
    prescription_ready    = "prescription_ready"
    general               = "general"


class MedicalRecordType(str, enum.Enum):
    lab_report    = "lab_report"
    prescription  = "prescription"
    xray          = "xray"
    scan          = "scan"
    discharge     = "discharge"
    other         = "other"


# ═══════════════════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════════════════

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Personal details
    date_of_birth = Column(Date, nullable=True)
    gender        = Column(String(20), nullable=True)
    blood_group   = Column(
        SAEnum(BloodGroup, name="blood_group_enum", create_type=True),
        nullable=True,
    )
    address       = Column(Text, nullable=True)
    city          = Column(String(100), nullable=True)
    state         = Column(String(100), nullable=True)
    pincode       = Column(String(10), nullable=True)
    emergency_contact_name   = Column(String(200), nullable=True)
    emergency_contact_phone  = Column(String(20), nullable=True)
    allergies     = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user          = relationship("User", backref="patient_profile", uselist=False)
    appointments  = relationship("Appointment", back_populates="patient", lazy="selectin")
    medical_records = relationship("MedicalRecord", back_populates="patient", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PatientProfile user_id={self.user_id}>"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Participants
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Scheduling
    appointment_date = Column(Date, nullable=False, index=True)
    slot_start_time  = Column(Time, nullable=False)
    slot_end_time    = Column(Time, nullable=False)
    consultation_type = Column(
        SAEnum(ConsultationType, name="consultation_type_enum", create_type=True),
        nullable=False,
        default=ConsultationType.in_clinic,
    )

    # Status
    status = Column(
        SAEnum(AppointmentStatus, name="appointment_status_enum", create_type=True),
        nullable=False,
        default=AppointmentStatus.pending,
        index=True,
    )

    # Details
    patient_notes   = Column(Text, nullable=True)   # Reason for visit
    doctor_notes    = Column(Text, nullable=True)   # Internal notes
    cancellation_reason = Column(Text, nullable=True)
    fee_charged     = Column(Numeric(10, 2), nullable=True)

    # Booking metadata
    booked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at  = Column(DateTime(timezone=True), nullable=True)
    completed_at  = Column(DateTime(timezone=True), nullable=True)
    cancelled_at  = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient       = relationship("PatientProfile", back_populates="appointments")
    doctor        = relationship("DoctorProfile", backref="appointments")
    clinic        = relationship("DoctorClinic", backref="appointments")
    status_history = relationship("AppointmentStatusHistory", back_populates="appointment", cascade="all, delete-orphan", lazy="selectin")
    prescription  = relationship("Prescription", back_populates="appointment", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Appointment {self.appointment_date} {self.slot_start_time} status={self.status.value}>"


class AppointmentStatusHistory(Base):
    __tablename__ = "appointment_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    note       = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    appointment = relationship("Appointment", back_populates="status_history")

    def __repr__(self) -> str:
        return f"<StatusHistory {self.old_status} → {self.new_status}>"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    diagnosis    = Column(Text, nullable=False)
    medicines    = Column(JSON, nullable=False, default=list)
    # medicines format: [{"name": "Paracetamol", "dosage": "500mg", "frequency": "TDS", "duration": "5 days", "notes": "after food"}]
    instructions = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    is_active    = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    appointment = relationship("Appointment", back_populates="prescription")
    doctor      = relationship("DoctorProfile", backref="prescriptions")
    patient     = relationship("PatientProfile", backref="prescriptions")

    def __repr__(self) -> str:
        return f"<Prescription appointment={self.appointment_id}>"


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patient_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    record_type  = Column(
        SAEnum(MedicalRecordType, name="medical_record_type_enum", create_type=True),
        nullable=False,
        default=MedicalRecordType.other,
    )
    title        = Column(String(300), nullable=False)
    description  = Column(Text, nullable=True)
    file_path    = Column(String(500), nullable=True)
    record_date  = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("PatientProfile", back_populates="medical_records")

    def __repr__(self) -> str:
        return f"<MedicalRecord {self.title}>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type = Column(
        SAEnum(NotificationType, name="notification_type_enum", create_type=True),
        nullable=False,
        default=NotificationType.general,
    )
    title   = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    data    = Column(JSON, nullable=True)  # e.g. {"appointment_id": "..."}
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Notification {self.title} read={self.is_read}>"
