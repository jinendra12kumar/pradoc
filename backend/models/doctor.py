"""
Doctor Onboarding & Verification — SQLAlchemy Models
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Time, Text, Integer, Numeric,
    Enum as SAEnum, ForeignKey, JSON, BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════

class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class QualificationType(str, enum.Enum):
    MBBS = "MBBS"
    BDS = "BDS"
    BHMS = "BHMS"
    BAMS = "BAMS"
    MD = "MD"
    MS = "MS"
    DM = "DM"
    MCh = "MCh"
    DNB = "DNB"
    OTHER = "OTHER"


class DocumentType(str, enum.Enum):
    MEDICAL_REG_CERT = "MEDICAL_REG_CERT"
    DEGREE_CERT = "DEGREE_CERT"
    PROFILE_PHOTO = "PROFILE_PHOTO"
    CLINIC_PROOF = "CLINIC_PROOF"
    GST_CERT = "GST_CERT"
    RENT_AGREEMENT = "RENT_AGREEMENT"
    UTILITY_BILL = "UTILITY_BILL"


class DocVerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class CouncilVerificationStatus(str, enum.Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class ClinicVerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class DayOfWeek(str, enum.Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"


class FlagType(str, enum.Enum):
    DUPLICATE_REG_NUMBER = "DUPLICATE_REG_NUMBER"
    DUPLICATE_DOCUMENT = "DUPLICATE_DOCUMENT"
    INVALID_GRADUATION_YEAR = "INVALID_GRADUATION_YEAR"
    EXPERIENCE_EXCEEDS_AGE = "EXPERIENCE_EXCEEDS_AGE"
    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    DUPLICATE_MOBILE = "DUPLICATE_MOBILE"


class FlagSeverity(str, enum.Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ═══════════════════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════════════════

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # ── Personal Info (Step 1) ────────────────────────────────────────────────
    profile_photo = Column(String(500), nullable=True)
    gender = Column(SAEnum(Gender, name="gender_enum", create_type=True), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    languages_spoken = Column(ARRAY(String), nullable=True)
    bio = Column(Text, nullable=True)

    # ── Professional Info (Step 2) ────────────────────────────────────────────
    medical_registration_number = Column(String(100), unique=True, nullable=True, index=True)
    medical_council = Column(String(200), nullable=True)
    registration_year = Column(Integer, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    current_hospital = Column(String(300), nullable=True)
    previous_hospitals = Column(ARRAY(String), nullable=True)

    # ── Primary specialization (Step 4) ───────────────────────────────────────
    primary_specialization = Column(String(200), nullable=True)

    # ── Council verification (future-ready) ───────────────────────────────────
    council_verification_status = Column(
        SAEnum(CouncilVerificationStatus, name="council_verif_enum", create_type=True),
        default=CouncilVerificationStatus.NOT_VERIFIED,
        nullable=False,
    )
    council_verified_at = Column(DateTime(timezone=True), nullable=True)
    council_reference_id = Column(String(200), nullable=True)

    # ── Completion tracking ───────────────────────────────────────────────────
    profile_completion_pct = Column(Integer, default=0, nullable=False)
    is_profile_complete = Column(Boolean, default=False, nullable=False)
    current_step = Column(Integer, default=1, nullable=False)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    user = relationship("User", backref="doctor_profile", uselist=False)
    qualifications = relationship("DoctorQualification", back_populates="profile", cascade="all, delete-orphan",lazy="selectin")
    specializations = relationship("DoctorSpecialization", back_populates="profile", cascade="all, delete-orphan",lazy="selectin")
    clinics = relationship("DoctorClinic", back_populates="profile", cascade="all, delete-orphan",lazy="selectin")
    documents = relationship("DoctorDocument", back_populates="profile", cascade="all, delete-orphan",lazy="selectin")
    verification = relationship("DoctorVerification", back_populates="profile", uselist=False, cascade="all, delete-orphan",lazy="selectin")
    flags = relationship("VerificationFlag", back_populates="profile", cascade="all, delete-orphan",lazy="selectin")

    def __repr__(self) -> str:
        return f"<DoctorProfile user_id={self.user_id}>"


class DoctorQualification(Base):
    __tablename__ = "doctor_qualifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    qualification_type = Column(
        SAEnum(QualificationType, name="qualification_type_enum", create_type=True),
        nullable=False,
    )
    college_name = Column(String(300), nullable=False)
    university_name = Column(String(300), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    profile = relationship("DoctorProfile", back_populates="qualifications")

    def __repr__(self) -> str:
        return f"<Qualification {self.qualification_type.value} - {self.college_name}>"


class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    specialization_name = Column(String(200), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    profile = relationship("DoctorProfile", back_populates="specializations")

    def __repr__(self) -> str:
        return f"<Specialization {self.specialization_name} primary={self.is_primary}>"


class DoctorClinic(Base):
    __tablename__ = "doctor_clinics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinic_name = Column(String(300), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    consultation_fee = Column(Numeric(10, 2), nullable=False)
    online_consultation = Column(Boolean, default=False, nullable=False)
    online_consultation_fee = Column(Numeric(10, 2), nullable=True)

    # ── Clinic verification (future-ready) ────────────────────────────────────
    clinic_verification_status = Column(
        SAEnum(ClinicVerificationStatus, name="clinic_verif_enum", create_type=True),
        default=ClinicVerificationStatus.PENDING,
        nullable=False,
    )
    clinic_verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    profile = relationship("DoctorProfile", back_populates="clinics")
    availability_slots = relationship("DoctorAvailability", back_populates="clinic", cascade="all, delete-orphan",lazy="selectin")

    def __repr__(self) -> str:
        return f"<Clinic {self.clinic_name} - {self.city}>"


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week = Column(
        SAEnum(DayOfWeek, name="day_of_week_enum", create_type=True),
        nullable=False,
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    clinic = relationship("DoctorClinic", back_populates="availability_slots")

    def __repr__(self) -> str:
        return f"<Availability {self.day_of_week.value} {self.start_time}-{self.end_time}>"


class DoctorDocument(Base):
    __tablename__ = "doctor_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type = Column(
        SAEnum(DocumentType, name="document_type_enum", create_type=True),
        nullable=False,
    )
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(128), nullable=False, index=True)
    original_filename = Column(String(300), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verification_status = Column(
        SAEnum(DocVerificationStatus, name="doc_verif_status_enum", create_type=True),
        default=DocVerificationStatus.PENDING,
        nullable=False,
    )

    profile = relationship("DoctorProfile", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.document_type.value} status={self.verification_status.value}>"


class DoctorVerification(Base):
    __tablename__ = "doctor_verification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    verification_status = Column(
        SAEnum(VerificationStatus, name="verification_status_enum", create_type=True),
        default=VerificationStatus.PENDING,
        nullable=False,
    )
    verification_score = Column(Integer, default=0, nullable=False)
    score_breakdown = Column(JSON, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    profile = relationship("DoctorProfile", back_populates="verification")

    def __repr__(self) -> str:
        return f"<Verification status={self.verification_status.value} score={self.verification_score}>"


class VerificationFlag(Base):
    __tablename__ = "verification_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    doctor_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flag_type = Column(
        SAEnum(FlagType, name="flag_type_enum", create_type=True),
        nullable=False,
    )
    severity = Column(
        SAEnum(FlagSeverity, name="flag_severity_enum", create_type=True),
        nullable=False,
    )
    description = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    profile = relationship("DoctorProfile", back_populates="flags")

    def __repr__(self) -> str:
        return f"<Flag {self.flag_type.value} severity={self.severity.value}>"
