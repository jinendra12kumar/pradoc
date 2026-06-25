"""
Doctor Onboarding — Pydantic V2 Schemas
"""
from __future__ import annotations

import re
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from models.doctor import (
    Gender,
    QualificationType,
    DocumentType,
    DocVerificationStatus,
    VerificationStatus,
    CouncilVerificationStatus,
    ClinicVerificationStatus,
    DayOfWeek,
    FlagType,
    FlagSeverity,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Predefined lists (shared with frontend)
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_COUNCILS = [
    "National Medical Commission",
    "Karnataka Medical Council",
    "Tamil Nadu Medical Council",
    "Delhi Medical Council",
    "Maharashtra Medical Council",
    "Other",
]

SPECIALIZATIONS = [
    "Cardiology",
    "Dermatology",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "Psychiatry",
    "Gynecology",
    "ENT",
    "General Physician",
    "Internal Medicine",
    "Diabetology",
    "Ophthalmology",
    "Urology",
    "Gastroenterology",
    "Pulmonology",
    "Oncology",
    "Nephrology",
    "Endocrinology",
    "Rheumatology",
    "Other",
]

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Delhi", "Chandigarh", "Puducherry",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1 — Personal Information
# ═══════════════════════════════════════════════════════════════════════════════

class PersonalInfoUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    gender: Gender
    date_of_birth: date
    languages_spoken: List[str] = Field(..., min_length=1)
    bio: Optional[str] = Field(None, max_length=2000)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        from datetime import date as dt
        today = dt.today()
        age = (today - v).days // 365
        if age < 22:
            raise ValueError("Doctor must be at least 22 years old")
        if age > 100:
            raise ValueError("Invalid date of birth")
        return v

    @field_validator("languages_spoken")
    @classmethod
    def validate_languages(cls, v: List[str]) -> List[str]:
        return [lang.strip() for lang in v if lang.strip()]


class PersonalInfoResponse(BaseModel):
    full_name: str
    email: str
    mobile: str
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    languages_spoken: Optional[List[str]] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 — Professional Information
# ═══════════════════════════════════════════════════════════════════════════════

class ProfessionalInfoUpdate(BaseModel):
    medical_registration_number: str = Field(..., min_length=3, max_length=100)
    medical_council: str = Field(..., max_length=200)
    registration_year: int
    years_of_experience: int = Field(..., ge=0, le=70)
    current_hospital: Optional[str] = Field(None, max_length=300)
    previous_hospitals: Optional[List[str]] = None

    @field_validator("registration_year")
    @classmethod
    def validate_reg_year(cls, v: int) -> int:
        from datetime import date
        current_year = date.today().year
        if v < 1950 or v > current_year:
            raise ValueError(f"Registration year must be between 1950 and {current_year}")
        return v

    @field_validator("medical_council")
    @classmethod
    def validate_council(cls, v: str) -> str:
        if v not in MEDICAL_COUNCILS:
            raise ValueError(f"Invalid medical council. Must be one of: {MEDICAL_COUNCILS}")
        return v


class ProfessionalInfoResponse(BaseModel):
    medical_registration_number: Optional[str] = None
    medical_council: Optional[str] = None
    registration_year: Optional[int] = None
    years_of_experience: Optional[int] = None
    current_hospital: Optional[str] = None
    previous_hospitals: Optional[List[str]] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3 — Qualifications
# ═══════════════════════════════════════════════════════════════════════════════

class QualificationCreate(BaseModel):
    qualification_type: QualificationType
    college_name: str = Field(..., min_length=2, max_length=300)
    university_name: str = Field(..., min_length=2, max_length=300)
    graduation_year: int

    @field_validator("graduation_year")
    @classmethod
    def validate_grad_year(cls, v: int) -> int:
        from datetime import date
        current_year = date.today().year
        if v < 1950 or v > current_year:
            raise ValueError(f"Graduation year must be between 1950 and {current_year}")
        return v


class QualificationResponse(BaseModel):
    id: UUID
    qualification_type: QualificationType
    college_name: str
    university_name: str
    graduation_year: int

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4 — Specializations
# ═══════════════════════════════════════════════════════════════════════════════

class SpecializationItem(BaseModel):
    specialization_name: str
    is_primary: bool = False

    @field_validator("specialization_name")
    @classmethod
    def validate_spec(cls, v: str) -> str:
        if v not in SPECIALIZATIONS:
            raise ValueError(f"Invalid specialization. Must be one of the predefined list.")
        return v


class SpecializationsUpdate(BaseModel):
    specializations: List[SpecializationItem] = Field(..., min_length=1)

    @field_validator("specializations")
    @classmethod
    def validate_primary(cls, v: List[SpecializationItem]) -> List[SpecializationItem]:
        primaries = [s for s in v if s.is_primary]
        if len(primaries) != 1:
            raise ValueError("Exactly one primary specialization is required")
        return v


class SpecializationResponse(BaseModel):
    id: UUID
    specialization_name: str
    is_primary: bool

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 5 — Clinic & Availability
# ═══════════════════════════════════════════════════════════════════════════════

class AvailabilitySlot(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    is_active: bool = True

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: time, info) -> time:
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("End time must be after start time")
        return v


class ClinicCreate(BaseModel):
    clinic_name: str = Field(..., min_length=2, max_length=300)
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., max_length=100)
    pincode: str = Field(..., min_length=6, max_length=6)
    consultation_fee: Decimal = Field(..., gt=0)
    online_consultation: bool = False
    online_consultation_fee: Optional[Decimal] = Field(None, gt=0)
    availability: List[AvailabilitySlot] = Field(default_factory=list)

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: str) -> str:
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Pincode must be exactly 6 digits")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        if v not in INDIAN_STATES:
            raise ValueError("Invalid state")
        return v


class ClinicUpdate(ClinicCreate):
    pass


class AvailabilityResponse(BaseModel):
    id: UUID
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    is_active: bool

    model_config = {"from_attributes": True}


class ClinicResponse(BaseModel):
    id: UUID
    clinic_name: str
    address: str
    city: str
    state: str
    pincode: str
    consultation_fee: Decimal
    online_consultation: bool
    online_consultation_fee: Optional[Decimal] = None
    clinic_verification_status: ClinicVerificationStatus
    availability_slots: List[AvailabilityResponse] = []

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 6 — Documents
# ═══════════════════════════════════════════════════════════════════════════════

class DocumentResponse(BaseModel):
    id: UUID
    document_type: DocumentType
    original_filename: str
    file_size: int
    uploaded_at: datetime
    verification_status: DocVerificationStatus

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Verification & Flags
# ═══════════════════════════════════════════════════════════════════════════════

class VerificationResponse(BaseModel):
    verification_status: VerificationStatus
    verification_score: int
    score_breakdown: Optional[dict] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    model_config = {"from_attributes": True}


class FlagResponse(BaseModel):
    id: UUID
    flag_type: FlagType
    severity: FlagSeverity
    description: str
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardResponse(BaseModel):
    profile_completion_pct: int
    verification_score: int
    verification_status: VerificationStatus
    current_step: int
    is_profile_complete: bool
    missing_fields: List[str]
    missing_documents: List[str]
    flags: List[FlagResponse]
    score_breakdown: Optional[dict] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Full Profile (aggregated)
# ═══════════════════════════════════════════════════════════════════════════════

class DoctorFullProfile(BaseModel):
    id: UUID
    user_id: UUID
    personal: PersonalInfoResponse
    professional: ProfessionalInfoResponse
    qualifications: List[QualificationResponse]
    specializations: List[SpecializationResponse]
    clinics: List[ClinicResponse]
    documents: List[DocumentResponse]
    verification: Optional[VerificationResponse] = None
    profile_completion_pct: int
    current_step: int
    is_profile_complete: bool


class DoctorPublicProfile(BaseModel):
    """What patients see — only approved doctors."""
    id: UUID
    full_name: str
    profile_photo: Optional[str] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    current_hospital: Optional[str] = None
    primary_specialization: Optional[str] = None
    specializations: List[str] = []
    qualifications: List[str] = []
    clinics: List[ClinicResponse] = []


# ═══════════════════════════════════════════════════════════════════════════════
# Reference Data
# ═══════════════════════════════════════════════════════════════════════════════

class ReferenceDataResponse(BaseModel):
    medical_councils: List[str]
    specializations: List[str]
    qualification_types: List[str]
    indian_states: List[str]
    document_types: List[str]
    days_of_week: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# Patient Portal — Doctor Search & Discovery
# ═══════════════════════════════════════════════════════════════════════════════

class DoctorSearchQuery(BaseModel):
    """Query parameters for patient doctor search."""
    q: Optional[str] = None
    specialization: Optional[str] = None
    min_experience: Optional[int] = Field(None, ge=0)
    max_experience: Optional[int] = Field(None, ge=0)
    min_fee: Optional[int] = Field(None, ge=0)
    max_fee: Optional[int] = Field(None, ge=0)
    gender: Optional[str] = None
    online_consultation: Optional[bool] = None
    city: Optional[str] = None
    availability_day: Optional[str] = None
    sort_by: Optional[str] = "experience"
    page: int = Field(1, ge=1)
    page_size: int = Field(12, ge=1, le=50)


class DoctorSearchResult(BaseModel):
    """Lightweight doctor card for search results."""
    id: UUID
    full_name: str
    profile_photo: Optional[str] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    primary_specialization: Optional[str] = None
    specializations: List[str] = []
    qualifications: List[str] = []
    consultation_fee: Optional[Decimal] = None
    online_consultation: bool = False
    online_consultation_fee: Optional[Decimal] = None
    clinic_city: Optional[str] = None
    clinic_name: Optional[str] = None
    languages_spoken: Optional[List[str]] = None


class DoctorSearchResponse(BaseModel):
    """Paginated search response."""
    doctors: List[DoctorSearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int


class SpecializationCount(BaseModel):
    """Specialization with doctor count for homepage cards."""
    name: str
    count: int
    icon: str


class TopClinic(BaseModel):
    """Top clinic summary for homepage."""
    clinic_name: str
    city: str
    state: str
    doctor_count: int
    specializations: List[str] = []


class PatientHomeData(BaseModel):
    """Aggregated homepage data for patient portal."""
    specializations: List[SpecializationCount]
    featured_doctors: List[DoctorSearchResult]
    top_clinics: List[TopClinic]


class DoctorDetailResponse(BaseModel):
    """Full doctor detail page for patients."""
    id: UUID
    full_name: str
    profile_photo: Optional[str] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    years_of_experience: Optional[int] = None
    current_hospital: Optional[str] = None
    primary_specialization: Optional[str] = None
    specializations: List[str] = []
    qualifications: List[QualificationResponse] = []
    clinics: List[ClinicResponse] = []
    languages_spoken: Optional[List[str]] = None
