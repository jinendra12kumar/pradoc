"""
Doctor Onboarding — Business Logic Layer

Handles profile steps, verification scoring, fraud detection, and dashboard.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.doctor import (
    DoctorProfile,
    DocumentType,
    VerificationStatus,
    FlagType,
    FlagSeverity,
)
from repositories.doctor_repo import DoctorRepository
from repositories.user_repo import UserRepository
from services.file_service import FileService
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
    FlagResponse,
    DoctorSearchQuery,
    DoctorSearchResult,
    DoctorSearchResponse,
    SpecializationCount,
    TopClinic,
    PatientHomeData,
    DoctorDetailResponse,
)

print("Loading DoctorService......")
class DoctorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = DoctorRepository(db)
        self.user_repo = UserRepository(db)
        self.file_svc = FileService()

    # ══════════════════════════════════════════════════════════════════════════
    # Profile access / creation
    # ══════════════════════════════════════════════════════════════════════════

    async def get_or_create_profile(self, user: User) -> DoctorProfile:
        profile = await self.repo.get_profile_by_user_id(user.id)
        if not profile:
            profile = await self.repo.create_profile(user.id)
            # Also create initial verification record
            await self.repo.create_or_update_verification(
                profile.id,
                verification_status=VerificationStatus.PENDING,
                verification_score=0,
            )
            # Refresh to load relationships
            profile = await self.repo.get_profile_by_user_id(user.id)
        return profile

    # ══════════════════════════════════════════════════════════════════════════
    # Step 1 — Personal Information
    # ══════════════════════════════════════════════════════════════════════════

    async def save_personal_info(
        self, user: User, data: PersonalInfoUpdate
    ) -> PersonalInfoResponse:
        profile = await self.get_or_create_profile(user)

        # Update user's full_name too
        user.full_name = data.full_name
        self.db.add(user)

        await self.repo.update_profile(
            profile,
            gender=data.gender,
            date_of_birth=data.date_of_birth,
            languages_spoken=data.languages_spoken,
            bio=data.bio,
            current_step=max(profile.current_step, 2),
        )

        await self._recalculate_completion(profile)

        return PersonalInfoResponse(
            full_name=user.full_name,
            email=user.email,
            mobile=user.mobile,
            gender=profile.gender,
            date_of_birth=profile.date_of_birth,
            languages_spoken=profile.languages_spoken,
            bio=profile.bio,
            profile_photo=profile.profile_photo,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Step 2 — Professional Information
    # ══════════════════════════════════════════════════════════════════════════

    async def save_professional_info(
        self, user: User, data: ProfessionalInfoUpdate
    ) -> ProfessionalInfoResponse:
        profile = await self.get_or_create_profile(user)

        # Check duplicate registration number
        existing = await self.repo.get_profile_by_reg_number(
            data.medical_registration_number, exclude_user_id=user.id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This medical registration number is already registered by another doctor.",
            )

        await self.repo.update_profile(
            profile,
            medical_registration_number=data.medical_registration_number,
            medical_council=data.medical_council,
            registration_year=data.registration_year,
            years_of_experience=data.years_of_experience,
            current_hospital=data.current_hospital,
            previous_hospitals=data.previous_hospitals,
            current_step=max(profile.current_step, 3),
        )

        await self._recalculate_completion(profile)

        return ProfessionalInfoResponse(
            medical_registration_number=profile.medical_registration_number,
            medical_council=profile.medical_council,
            registration_year=profile.registration_year,
            years_of_experience=profile.years_of_experience,
            current_hospital=profile.current_hospital,
            previous_hospitals=profile.previous_hospitals,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Step 3 — Qualifications
    # ══════════════════════════════════════════════════════════════════════════

    async def add_qualification(
        self, user: User, data: QualificationCreate
    ) -> QualificationResponse:
        profile = await self.get_or_create_profile(user)

        qual = await self.repo.add_qualification(
            profile.id,
            qualification_type=data.qualification_type,
            college_name=data.college_name,
            university_name=data.university_name,
            graduation_year=data.graduation_year,
        )

        await self.repo.update_profile(
            profile, current_step=max(profile.current_step, 4)
        )
        await self._recalculate_completion(profile)

        return QualificationResponse.model_validate(qual)

    async def delete_qualification(self, user: User, qual_id: UUID) -> dict:
        profile = await self.get_or_create_profile(user)
        deleted = await self.repo.delete_qualification(qual_id, profile.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Qualification not found.")
        await self._recalculate_completion(profile)
        return {"message": "Qualification removed."}

    async def get_qualifications(self, user: User) -> List[QualificationResponse]:
        profile = await self.get_or_create_profile(user)
        quals = await self.repo.get_qualifications(profile.id)
        return [QualificationResponse.model_validate(q) for q in quals]

    # ══════════════════════════════════════════════════════════════════════════
    # Step 4 — Specializations
    # ══════════════════════════════════════════════════════════════════════════

    async def save_specializations(
        self, user: User, data: SpecializationsUpdate
    ) -> List[SpecializationResponse]:
        profile = await self.get_or_create_profile(user)

        specs_data = [s.model_dump() for s in data.specializations]
        specs = await self.repo.set_specializations(profile.id, specs_data)

        # Update primary specialization on profile
        primary = next((s for s in data.specializations if s.is_primary), None)
        if primary:
            fresh_profile = await self.repo.get_profile_by_user_id(user.id)
            await self.repo.update_profile(
                profile,
                primary_specialization=primary.specialization_name,
                current_step=max(fresh_profile.current_step, 5),
            )

        await self._recalculate_completion(profile)

        return [SpecializationResponse.model_validate(s) for s in specs]

    # ══════════════════════════════════════════════════════════════════════════
    # Step 5 — Practice / Clinic
    # ══════════════════════════════════════════════════════════════════════════

    async def create_clinic(self, user: User, data: ClinicCreate) -> ClinicResponse:
        profile = await self.get_or_create_profile(user)

        clinic_data = data.model_dump()
        # Convert availability time objects properly
        availability = clinic_data.pop("availability", [])
        avail_dicts = []
        for slot in availability:
            avail_dicts.append({
                "day_of_week": slot["day_of_week"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"],
                "is_active": slot.get("is_active", True),
            })

        clinic = await self.repo.create_clinic(
            profile.id, availability=avail_dicts, **clinic_data
        )
        # response=ClinicResponse.model_validate(clinic)

        await self.repo.update_profile(
            profile, current_step=max(profile.current_step, 6)
        )
        await self._recalculate_completion(profile)
        
        clinic = await self.repo.get_clinic_by_id(clinic.id)
        return ClinicResponse.model_validate(clinic)

    async def update_clinic(
        self, user: User, clinic_id: UUID, data: ClinicUpdate
    ) -> ClinicResponse:
        profile = await self.get_or_create_profile(user)

        clinic_data = data.model_dump()
        availability = clinic_data.pop("availability", [])
        avail_dicts = []
        for slot in availability:
            avail_dicts.append({
                "day_of_week": slot["day_of_week"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"],
                "is_active": slot.get("is_active", True),
            })

        clinic = await self.repo.update_clinic(
            clinic_id, profile.id, availability=avail_dicts, **clinic_data
        )
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found.")

        await self._recalculate_completion(profile)
        
        return ClinicResponse.model_validate(clinic)

    async def delete_clinic(self, user: User, clinic_id: UUID) -> dict:
        profile = await self.get_or_create_profile(user)
        deleted = await self.repo.delete_clinic(clinic_id, profile.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Clinic not found.")
        await self._recalculate_completion(profile)
        return {"message": "Clinic removed."}

    # ══════════════════════════════════════════════════════════════════════════
    # Step 6 — Documents
    # ══════════════════════════════════════════════════════════════════════════

    async def upload_document(
        self, user: User, document_type: DocumentType, file: UploadFile
    ) -> DocumentResponse:
        profile = await self.get_or_create_profile(user)

        # Save file
        file_path, file_hash, file_size = await self.file_svc.save_upload(
            file, str(profile.id), subfolder="documents"
        )

        # Check duplicate hash across other profiles
        dup = await self.repo.find_document_by_hash(file_hash, exclude_profile_id=profile.id)
        if dup:
            await self.repo.create_flag(
                profile.id,
                FlagType.DUPLICATE_DOCUMENT,
                FlagSeverity.CRITICAL,
                f"Uploaded {document_type.value} has identical hash to document from another doctor profile.",
            )

        # Delete old document of same type if exists
        existing = await self.repo.get_document_by_type(profile.id, document_type)
        if existing:
            await self.file_svc.delete_file(existing.file_path)
            await self.repo.delete_document(existing.id, profile.id)

        doc = await self.repo.create_document(
            profile.id,
            document_type=document_type,
            file_path=file_path,
            file_hash=file_hash,
            original_filename=file.filename,
            file_size=file_size,
        )

        await self._recalculate_completion(profile)
        return DocumentResponse.model_validate(doc)

    async def upload_profile_photo(self, user: User, file: UploadFile) -> dict:
        profile = await self.get_or_create_profile(user)

        file_path, _, _ = await self.file_svc.save_upload(
            file, str(profile.id), subfolder="photos"
        )

        # Delete old photo
        if profile.profile_photo:
            await self.file_svc.delete_file(profile.profile_photo)

        await self.repo.update_profile(profile, profile_photo=file_path)
        await self._recalculate_completion(profile)

        return {"profile_photo": file_path}

    async def delete_document(self, user: User, doc_id: UUID) -> dict:
        profile = await self.get_or_create_profile(user)
        docs = await self.repo.get_documents(profile.id)
        doc = next((d for d in docs if d.id == doc_id), None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        await self.file_svc.delete_file(doc.file_path)
        await self.repo.delete_document(doc_id, profile.id)
        await self._recalculate_completion(profile)
        return {"message": "Document deleted."}

    # ══════════════════════════════════════════════════════════════════════════
    # Submit for verification
    # ══════════════════════════════════════════════════════════════════════════

    async def submit_for_verification(self, user: User) -> VerificationResponse:
        profile = await self.get_or_create_profile(user)

        # Run fraud checks first
        await self._run_fraud_checks(profile, user)

        # Calculate score
        score, breakdown = await self._calculate_verification_score(profile)

        # Determine status
        flags = await self.repo.get_flags(profile.id)
        critical_flags = [f for f in flags if f.severity == FlagSeverity.CRITICAL and not f.is_resolved]

        if critical_flags:
            v_status = VerificationStatus.UNDER_REVIEW
        elif score >= 80:
            v_status = VerificationStatus.APPROVED
        elif score >= 50:
            v_status = VerificationStatus.UNDER_REVIEW
        else:
            v_status = VerificationStatus.REJECTED

        verification = await self.repo.create_or_update_verification(
            profile.id,
            verification_status=v_status,
            verification_score=score,
            score_breakdown=breakdown,
        )

        # Mark profile complete if approved
        await self.repo.update_profile(
            profile,
            is_profile_complete=(v_status == VerificationStatus.APPROVED),
        )

        return VerificationResponse.model_validate(verification)

    # ══════════════════════════════════════════════════════════════════════════
    # Full profile + Dashboard
    # ══════════════════════════════════════════════════════════════════════════

    async def get_full_profile(self, user: User) -> DoctorFullProfile:
        profile = await self.get_or_create_profile(user)

        return DoctorFullProfile(
            id=profile.id,
            user_id=profile.user_id,
            personal=PersonalInfoResponse(
                full_name=user.full_name,
                email=user.email,
                mobile=user.mobile,
                gender=profile.gender,
                date_of_birth=profile.date_of_birth,
                languages_spoken=profile.languages_spoken,
                bio=profile.bio,
                profile_photo=profile.profile_photo,
            ),
            professional=ProfessionalInfoResponse(
                medical_registration_number=profile.medical_registration_number,
                medical_council=profile.medical_council,
                registration_year=profile.registration_year,
                years_of_experience=profile.years_of_experience,
                current_hospital=profile.current_hospital,
                previous_hospitals=profile.previous_hospitals,
            ),
            qualifications=[
                QualificationResponse.model_validate(q) for q in profile.qualifications
            ],
            specializations=[
                SpecializationResponse.model_validate(s) for s in profile.specializations
            ],
            clinics=[
                ClinicResponse.model_validate(c) for c in profile.clinics
            ],
            documents=[
                DocumentResponse.model_validate(d) for d in profile.documents
            ],
            verification=(
                VerificationResponse.model_validate(profile.verification)
                if profile.verification
                else None
            ),
            profile_completion_pct=profile.profile_completion_pct,
            current_step=profile.current_step,
            is_profile_complete=profile.is_profile_complete,
        )

    async def get_dashboard(self, user: User) -> DashboardResponse:
        profile = await self.get_or_create_profile(user)

        missing_fields = self._get_missing_fields(profile, user)
        missing_documents = self._get_missing_documents(profile)

        verification = profile.verification
        flags = [FlagResponse.model_validate(f) for f in profile.flags] if profile.flags else []

        return DashboardResponse(
            profile_completion_pct=profile.profile_completion_pct,
            verification_score=verification.verification_score if verification else 0,
            verification_status=(
                verification.verification_status if verification else VerificationStatus.PENDING
            ),
            current_step=profile.current_step,
            is_profile_complete=profile.is_profile_complete,
            missing_fields=missing_fields,
            missing_documents=missing_documents,
            flags=flags,
            score_breakdown=verification.score_breakdown if verification else None,
        )

    async def get_public_profile(self, doctor_profile_id: UUID) -> DoctorPublicProfile:
        profile = await self.repo.get_profile_by_id(doctor_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        # Enforce visibility rules
        if not profile.is_profile_complete:
            raise HTTPException(status_code=404, detail="Doctor not found.")
        if profile.verification and profile.verification.verification_status != VerificationStatus.APPROVED:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        user = profile.user
        if not user.is_verified or not user.is_active:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        return DoctorPublicProfile(
            id=profile.id,
            full_name=user.full_name,
            profile_photo=profile.profile_photo,
            gender=profile.gender,
            bio=profile.bio,
            years_of_experience=profile.years_of_experience,
            current_hospital=profile.current_hospital,
            primary_specialization=profile.primary_specialization,
            specializations=[s.specialization_name for s in profile.specializations],
            qualifications=[
                f"{q.qualification_type.value} - {q.college_name}" for q in profile.qualifications
            ],
            clinics=[ClinicResponse.model_validate(c) for c in profile.clinics],
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Scoring Engine
    # ══════════════════════════════════════════════════════════════════════════

    async def _calculate_verification_score(
        self, profile: DoctorProfile
    ) -> tuple[int, dict]:
        breakdown = {
            "registration_number": 0,
            "qualification": 0,
            "registration_certificate": 0,
            "degree_certificate": 0,
            "clinic_information": 0,
        }

        # Registration Number (+20)
        if profile.medical_registration_number:
            breakdown["registration_number"] = 20

        # Qualification Added (+20)
        quals = await self.repo.get_qualifications(profile.id)
        if quals:
            breakdown["qualification"] = 20

        # Registration Certificate Uploaded (+30)
        docs = await self.repo.get_documents(profile.id)
        doc_types = {d.document_type for d in docs}
        if DocumentType.MEDICAL_REG_CERT in doc_types:
            breakdown["registration_certificate"] = 30

        # Degree Certificate Uploaded (+20)
        if DocumentType.DEGREE_CERT in doc_types:
            breakdown["degree_certificate"] = 20

        # Clinic Information (+10)
        clinics = await self.repo.get_clinics(profile.id)
        if clinics:
            breakdown["clinic_information"] = 10

        total = sum(breakdown.values())
        return total, breakdown

    # ══════════════════════════════════════════════════════════════════════════
    # Fraud Detection
    # ══════════════════════════════════════════════════════════════════════════

    async def _run_fraud_checks(self, profile: DoctorProfile, user: User) -> None:
        # Clear old unresolved flags before re-running
        await self.repo.clear_unresolved_flags(profile.id)

        # 1. Duplicate Registration Number
        if profile.medical_registration_number:
            dup_reg = await self.repo.get_profile_by_reg_number(
                profile.medical_registration_number, exclude_user_id=user.id
            )
            if dup_reg:
                await self.repo.create_flag(
                    profile.id,
                    FlagType.DUPLICATE_REG_NUMBER,
                    FlagSeverity.CRITICAL,
                    f"Registration number '{profile.medical_registration_number}' is already in use by another doctor.",
                )

        # 2. Duplicate Document Hash
        docs = await self.repo.get_documents(profile.id)
        for doc in docs:
            dup_doc = await self.repo.find_document_by_hash(
                doc.file_hash, exclude_profile_id=profile.id
            )
            if dup_doc:
                await self.repo.create_flag(
                    profile.id,
                    FlagType.DUPLICATE_DOCUMENT,
                    FlagSeverity.CRITICAL,
                    f"Document '{doc.original_filename}' has identical hash to a document from another doctor.",
                )

        # 3. Invalid Graduation Year
        quals = await self.repo.get_qualifications(profile.id)
        current_year = date.today().year
        for q in quals:
            if q.graduation_year > current_year or q.graduation_year < 1950:
                await self.repo.create_flag(
                    profile.id,
                    FlagType.INVALID_GRADUATION_YEAR,
                    FlagSeverity.WARNING,
                    f"Qualification '{q.qualification_type.value}' has invalid graduation year: {q.graduation_year}.",
                )

        # 4. Experience exceeds age
        if profile.date_of_birth and profile.years_of_experience:
            age = (date.today() - profile.date_of_birth).days // 365
            # Minimum age to start practicing is ~22 (MBBS graduation)
            max_experience = age - 22
            if profile.years_of_experience > max_experience:
                await self.repo.create_flag(
                    profile.id,
                    FlagType.EXPERIENCE_EXCEEDS_AGE,
                    FlagSeverity.WARNING,
                    f"Claimed {profile.years_of_experience} years experience but age is {age}. "
                    f"Maximum plausible experience: {max_experience} years.",
                )

    # ══════════════════════════════════════════════════════════════════════════
    # Completion calculation
    # ══════════════════════════════════════════════════════════════════════════

    async def _recalculate_completion(self, profile: DoctorProfile) -> None:
        """Recalculate profile_completion_pct and update profile."""
        # Reload to get fresh relationships
        profile = await self.repo.get_profile_by_user_id(profile.user_id)
        user = await self.user_repo.get_by_id(str(profile.user_id))

        total_items = 12
        completed = 0

        # Step 1: Personal
        if user and user.full_name:
            completed += 1
        if profile.gender:
            completed += 1
        if profile.date_of_birth:
            completed += 1
        if profile.languages_spoken and len(profile.languages_spoken) > 0:
            completed += 1

        # Step 2: Professional
        if profile.medical_registration_number:
            completed += 1
        if profile.medical_council:
            completed += 1
        if profile.years_of_experience is not None:
            completed += 1

        # Step 3: Qualifications
        if profile.qualifications and len(profile.qualifications) > 0:
            completed += 1

        # Step 4: Specializations
        if profile.specializations and len(profile.specializations) > 0:
            completed += 1

        # Step 5: Clinic
        if profile.clinics and len(profile.clinics) > 0:
            completed += 1

        # Step 6: Documents (need at least reg cert + degree)
        if profile.documents:
            doc_types = {d.document_type for d in profile.documents}
            if DocumentType.MEDICAL_REG_CERT in doc_types:
                completed += 1
            if DocumentType.DEGREE_CERT in doc_types:
                completed += 1

        pct = int((completed / total_items) * 100)
        await self.repo.update_profile(profile, profile_completion_pct=pct)

    # ══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _get_missing_fields(self, profile: DoctorProfile, user: User) -> List[str]:
        missing = []
        if not profile.gender:
            missing.append("Gender")
        if not profile.date_of_birth:
            missing.append("Date of Birth")
        if not profile.languages_spoken:
            missing.append("Languages Spoken")
        if not profile.medical_registration_number:
            missing.append("Medical Registration Number")
        if not profile.medical_council:
            missing.append("Medical Council")
        if profile.years_of_experience is None:
            missing.append("Years of Experience")
        if not profile.qualifications or len(profile.qualifications) == 0:
            missing.append("Qualifications")
        if not profile.specializations or len(profile.specializations) == 0:
            missing.append("Specializations")
        if not profile.clinics or len(profile.clinics) == 0:
            missing.append("Clinic Information")
        if not profile.profile_photo:
            missing.append("Profile Photo")
        return missing

    def _get_missing_documents(self, profile: DoctorProfile) -> List[str]:
        missing = []
        doc_types = (
            {d.document_type for d in profile.documents}
            if profile.documents
            else set()
        )
        mandatory = {
            DocumentType.MEDICAL_REG_CERT: "Medical Registration Certificate",
            DocumentType.DEGREE_CERT: "Degree Certificate",
            DocumentType.PROFILE_PHOTO: "Profile Photo (Verification Copy)",
        }
        for dt, label in mandatory.items():
            if dt not in doc_types:
                missing.append(label)
        return missing

    # ══════════════════════════════════════════════════════════════════════════
    # Patient Portal — Doctor Search & Discovery
    # ══════════════════════════════════════════════════════════════════════════

    SPECIALIZATION_ICONS = {
        "Cardiology": "❤️",
        "Dermatology": "🧴",
        "Neurology": "🧠",
        "Orthopedics": "🦴",
        "Pediatrics": "👶",
        "Psychiatry": "🧘",
        "Gynecology": "🤰",
        "ENT": "👂",
        "General Physician": "🩺",
        "Internal Medicine": "💊",
        "Diabetology": "🩸",
        "Ophthalmology": "👁️",
        "Urology": "🫘",
        "Gastroenterology": "🫄",
        "Pulmonology": "🫁",
        "Oncology": "🎗️",
        "Nephrology": "🫀",
        "Endocrinology": "⚗️",
        "Rheumatology": "🦵",
        "Other": "➕",
    }

    def _profile_to_search_result(self, profile: DoctorProfile) -> DoctorSearchResult:
        """Convert a DoctorProfile ORM object to a DoctorSearchResult schema."""
        user = profile.user
        first_clinic = profile.clinics[0] if profile.clinics else None

        return DoctorSearchResult(
            id=profile.id,
            full_name=user.full_name if user else "Unknown",
            profile_photo=profile.profile_photo,
            gender=profile.gender,
            bio=profile.bio,
            years_of_experience=profile.years_of_experience,
            primary_specialization=profile.primary_specialization,
            specializations=[s.specialization_name for s in profile.specializations],
            qualifications=[
                f"{q.qualification_type.value} - {q.college_name}" for q in profile.qualifications
            ],
            consultation_fee=first_clinic.consultation_fee if first_clinic else None,
            online_consultation=any(c.online_consultation for c in profile.clinics),
            online_consultation_fee=(
                first_clinic.online_consultation_fee if first_clinic and first_clinic.online_consultation else None
            ),
            clinic_city=first_clinic.city if first_clinic else None,
            clinic_name=first_clinic.clinic_name if first_clinic else None,
            languages_spoken=profile.languages_spoken,
        )

    async def search_doctors(self, query: DoctorSearchQuery) -> DoctorSearchResponse:
        """Search approved doctors with filters and pagination."""
        offset = (query.page - 1) * query.page_size

        profiles, total = await self.repo.search_doctors(
            q=query.q,
            specialization=query.specialization,
            min_experience=query.min_experience,
            max_experience=query.max_experience,
            min_fee=query.min_fee,
            max_fee=query.max_fee,
            gender=query.gender,
            online_consultation=query.online_consultation,
            city=query.city,
            availability_day=query.availability_day,
            sort_by=query.sort_by,
            offset=offset,
            limit=query.page_size,
        )

        doctors = [self._profile_to_search_result(p) for p in profiles]
        total_pages = max(1, -(-total // query.page_size))  # ceiling division

        return DoctorSearchResponse(
            doctors=doctors,
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages,
        )

    async def get_patient_home_data(self) -> PatientHomeData:
        """Assemble homepage data: specialization counts, featured doctors, top clinics."""
        # Specialization counts with icons
        raw_specs = await self.repo.get_specialization_counts()
        specializations = [
            SpecializationCount(
                name=s["name"],
                count=s["count"],
                icon=self.SPECIALIZATION_ICONS.get(s["name"], "🏥"),
            )
            for s in raw_specs
        ]

        # Featured doctors
        featured_profiles = await self.repo.get_featured_doctors(limit=8)
        featured_doctors = [self._profile_to_search_result(p) for p in featured_profiles]

        # Top clinics
        raw_clinics = await self.repo.get_top_clinics(limit=6)
        top_clinics = [TopClinic(**c) for c in raw_clinics]

        return PatientHomeData(
            specializations=specializations,
            featured_doctors=featured_doctors,
            top_clinics=top_clinics,
        )

    async def get_doctor_detail(self, doctor_profile_id: UUID) -> DoctorDetailResponse:
        """Full doctor detail for patient view — only approved doctors visible."""
        profile = await self.repo.get_profile_by_id(doctor_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        # Enforce visibility rules
        if not profile.is_profile_complete:
            raise HTTPException(status_code=404, detail="Doctor not found.")
        if profile.verification and profile.verification.verification_status != VerificationStatus.APPROVED:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        user = profile.user
        if not user or not user.is_verified or not user.is_active:
            raise HTTPException(status_code=404, detail="Doctor not found.")

        return DoctorDetailResponse(
            id=profile.id,
            full_name=user.full_name,
            profile_photo=profile.profile_photo,
            gender=profile.gender,
            bio=profile.bio,
            years_of_experience=profile.years_of_experience,
            current_hospital=profile.current_hospital,
            primary_specialization=profile.primary_specialization,
            specializations=[s.specialization_name for s in profile.specializations],
            qualifications=[
                QualificationResponse.model_validate(q) for q in profile.qualifications
            ],
            clinics=[ClinicResponse.model_validate(c) for c in profile.clinics],
            languages_spoken=profile.languages_spoken,
        )
