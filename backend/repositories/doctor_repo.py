"""
Doctor Onboarding — Data Access Layer
"""
from __future__ import annotations

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.doctor import (
    DoctorProfile,
    DoctorQualification,
    DoctorSpecialization,
    DoctorClinic,
    DoctorAvailability,
    DoctorDocument,
    DoctorVerification,
    VerificationFlag,
    VerificationStatus,
    DocumentType,
    FlagType,
    FlagSeverity,
)


class DoctorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[DoctorProfile]:
        result = await self.db.execute(
            select(DoctorProfile)
            .options(
                selectinload(DoctorProfile.qualifications),
                selectinload(DoctorProfile.specializations),
                selectinload(DoctorProfile.clinics).selectinload(DoctorClinic.availability_slots),
                selectinload(DoctorProfile.documents),
                selectinload(DoctorProfile.verification),
                selectinload(DoctorProfile.flags),
                selectinload(DoctorProfile.user),
            )
            .where(DoctorProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_id(self, profile_id: UUID) -> Optional[DoctorProfile]:
        result = await self.db.execute(
            select(DoctorProfile)
            .options(
                selectinload(DoctorProfile.qualifications),
                selectinload(DoctorProfile.specializations),
                selectinload(DoctorProfile.clinics).selectinload(DoctorClinic.availability_slots),
                selectinload(DoctorProfile.documents),
                selectinload(DoctorProfile.verification),
                selectinload(DoctorProfile.flags),
                selectinload(DoctorProfile.user),
            )
            .where(DoctorProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def create_profile(self, user_id: UUID) -> DoctorProfile:
        profile = DoctorProfile(user_id=user_id)
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_profile(self, profile: DoctorProfile, **kwargs) -> DoctorProfile:
        for key, value in kwargs.items():
            setattr(profile, key, value)
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    # ── Duplicate checks ──────────────────────────────────────────────────────

    async def get_profile_by_reg_number(
        self, reg_number: str, exclude_user_id: Optional[UUID] = None
    ) -> Optional[DoctorProfile]:
        stmt = select(DoctorProfile).where(
            DoctorProfile.medical_registration_number == reg_number
        )
        if exclude_user_id:
            stmt = stmt.where(DoctorProfile.user_id != exclude_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ── Qualifications ────────────────────────────────────────────────────────

    async def add_qualification(
        self, profile_id: UUID, **kwargs
    ) -> DoctorQualification:
        qual = DoctorQualification(doctor_profile_id=profile_id, **kwargs)
        self.db.add(qual)
        await self.db.flush()
        await self.db.refresh(qual)
        return qual

    async def get_qualifications(self, profile_id: UUID) -> List[DoctorQualification]:
        result = await self.db.execute(
            select(DoctorQualification).where(
                DoctorQualification.doctor_profile_id == profile_id
            )
        )
        return list(result.scalars().all())

    async def delete_qualification(self, qual_id: UUID, profile_id: UUID) -> bool:
        result = await self.db.execute(
            delete(DoctorQualification).where(
                and_(
                    DoctorQualification.id == qual_id,
                    DoctorQualification.doctor_profile_id == profile_id,
                )
            )
        )
        await self.db.flush()
        return result.rowcount > 0

    # ── Specializations ───────────────────────────────────────────────────────

    async def set_specializations(
        self, profile_id: UUID, specs: list
    ) -> List[DoctorSpecialization]:
        # Delete existing
        await self.db.execute(
            delete(DoctorSpecialization).where(
                DoctorSpecialization.doctor_profile_id == profile_id
            )
        )
        new_specs = []
        for s in specs:
            spec = DoctorSpecialization(
                doctor_profile_id=profile_id,
                specialization_name=s["specialization_name"],
                is_primary=s["is_primary"],
            )
            self.db.add(spec)
            new_specs.append(spec)
        await self.db.flush()
        for spec in new_specs:
            await self.db.refresh(spec)
        return new_specs

    # ── Clinics ───────────────────────────────────────────────────────────────

    async def create_clinic(self, profile_id: UUID, **kwargs) -> DoctorClinic:
        availability_data = kwargs.pop("availability", [])
        clinic = DoctorClinic(doctor_profile_id=profile_id, **kwargs)
        self.db.add(clinic)
        await self.db.flush()
        await self.db.refresh(clinic)

        # Add availability slots
        if availability_data:
            for slot_data in availability_data:
                slot = DoctorAvailability(
                    clinic_id=clinic.id,
                    day_of_week=slot_data["day_of_week"],
                    start_time=slot_data["start_time"],
                    end_time=slot_data["end_time"],
                    is_active=slot_data.get("is_active", True),
                )
                self.db.add(slot)
            await self.db.flush()

        return await self.get_clinic_by_id(clinic.id)

    async def update_clinic(self, clinic_id: UUID, profile_id: UUID, **kwargs) -> Optional[DoctorClinic]:
        result = await self.db.execute(
            select(DoctorClinic).where(
                and_(
                    DoctorClinic.id == clinic_id,
                    DoctorClinic.doctor_profile_id == profile_id,
                )
            )
        )
        clinic = result.scalar_one_or_none()
        if not clinic:
            return None

        availability_data = kwargs.pop("availability", None)
        for key, value in kwargs.items():
            setattr(clinic, key, value)
        self.db.add(clinic)

        if availability_data is not None:
            await self.db.execute(
                delete(DoctorAvailability).where(
                    DoctorAvailability.clinic_id == clinic_id
                )
            )
            for slot_data in availability_data:
                slot = DoctorAvailability(
                    clinic_id=clinic_id,
                    day_of_week=slot_data["day_of_week"],
                    start_time=slot_data["start_time"],
                    end_time=slot_data["end_time"],
                    is_active=slot_data.get("is_active", True),
                )
                self.db.add(slot)

        await self.db.flush()
        return await self.get_clinic_by_id(clinic_id)

    async def get_clinic_by_id(self, clinic_id: UUID) -> Optional[DoctorClinic]:
        result = await self.db.execute(
            select(DoctorClinic)
            .options(selectinload(DoctorClinic.availability_slots))
            .where(DoctorClinic.id == clinic_id)
        )
        return result.scalar_one_or_none()

    async def get_clinics(self, profile_id: UUID) -> List[DoctorClinic]:
        result = await self.db.execute(
            select(DoctorClinic)
            .options(selectinload(DoctorClinic.availability_slots))
            .where(DoctorClinic.doctor_profile_id == profile_id)
        )
        return list(result.scalars().all())

    async def delete_clinic(self, clinic_id: UUID, profile_id: UUID) -> bool:
        result = await self.db.execute(
            delete(DoctorClinic).where(
                and_(
                    DoctorClinic.id == clinic_id,
                    DoctorClinic.doctor_profile_id == profile_id,
                )
            )
        )
        await self.db.flush()
        return result.rowcount > 0

    # ── Documents ─────────────────────────────────────────────────────────────

    async def create_document(self, profile_id: UUID, **kwargs) -> DoctorDocument:
        doc = DoctorDocument(doctor_profile_id=profile_id, **kwargs)
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_documents(self, profile_id: UUID) -> List[DoctorDocument]:
        result = await self.db.execute(
            select(DoctorDocument).where(
                DoctorDocument.doctor_profile_id == profile_id
            )
        )
        return list(result.scalars().all())

    async def get_document_by_type(
        self, profile_id: UUID, doc_type: DocumentType
    ) -> Optional[DoctorDocument]:
        result = await self.db.execute(
            select(DoctorDocument).where(
                and_(
                    DoctorDocument.doctor_profile_id == profile_id,
                    DoctorDocument.document_type == doc_type,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_document_by_hash(
        self, file_hash: str, exclude_profile_id: Optional[UUID] = None
    ) -> Optional[DoctorDocument]:
        stmt = select(DoctorDocument).where(DoctorDocument.file_hash == file_hash)
        if exclude_profile_id:
            stmt = stmt.where(
                DoctorDocument.doctor_profile_id != exclude_profile_id
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_document(self, doc_id: UUID, profile_id: UUID) -> bool:
        result = await self.db.execute(
            delete(DoctorDocument).where(
                and_(
                    DoctorDocument.id == doc_id,
                    DoctorDocument.doctor_profile_id == profile_id,
                )
            )
        )
        await self.db.flush()
        return result.rowcount > 0

    # ── Verification ──────────────────────────────────────────────────────────

    async def get_verification(self, profile_id: UUID) -> Optional[DoctorVerification]:
        result = await self.db.execute(
            select(DoctorVerification).where(
                DoctorVerification.doctor_profile_id == profile_id
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update_verification(
        self, profile_id: UUID, **kwargs
    ) -> DoctorVerification:
        verification = await self.get_verification(profile_id)
        if verification:
            for key, value in kwargs.items():
                setattr(verification, key, value)
            self.db.add(verification)
        else:
            verification = DoctorVerification(
                doctor_profile_id=profile_id, **kwargs
            )
            self.db.add(verification)
        await self.db.flush()
        await self.db.refresh(verification)
        return verification

    # ── Flags ─────────────────────────────────────────────────────────────────

    async def create_flag(
        self,
        profile_id: UUID,
        flag_type: FlagType,
        severity: FlagSeverity,
        description: str,
    ) -> VerificationFlag:
        flag = VerificationFlag(
            doctor_profile_id=profile_id,
            flag_type=flag_type,
            severity=severity,
            description=description,
        )
        self.db.add(flag)
        await self.db.flush()
        await self.db.refresh(flag)
        return flag

    async def get_flags(self, profile_id: UUID) -> List[VerificationFlag]:
        result = await self.db.execute(
            select(VerificationFlag).where(
                VerificationFlag.doctor_profile_id == profile_id
            )
        )
        return list(result.scalars().all())

    async def clear_unresolved_flags(self, profile_id: UUID) -> None:
        await self.db.execute(
            delete(VerificationFlag).where(
                and_(
                    VerificationFlag.doctor_profile_id == profile_id,
                    VerificationFlag.is_resolved == False,
                )
            )
        )
        await self.db.flush()

    # ── Verified doctor search (patient-facing) ──────────────────────────────

    async def search_doctors(
        self,
        q: str = None,
        specialization: str = None,
        min_experience: int = None,
        max_experience: int = None,
        min_fee: int = None,
        max_fee: int = None,
        gender: str = None,
        online_consultation: bool = None,
        city: str = None,
        availability_day: str = None,
        sort_by: str = "experience",
        offset: int = 0,
        limit: int = 12,
    ) -> tuple[list, int]:
        """Search approved doctors with filters. Returns (profiles, total_count)."""
        from models.user import User
        from sqlalchemy import func as sa_func, or_

        base_conditions = [
            User.is_verified == True,
            User.is_active == True,
            DoctorProfile.is_profile_complete == True,
            DoctorVerification.verification_status == VerificationStatus.APPROVED,
        ]

        # Build WHERE clause
        conditions = list(base_conditions)

        if q:
            search_term = f"%{q.lower()}%"
            conditions.append(
                or_(
                    sa_func.lower(User.full_name).like(search_term),
                    sa_func.lower(DoctorProfile.primary_specialization).like(search_term),
                )
            )

        if specialization:
            conditions.append(
                DoctorProfile.primary_specialization == specialization
            )

        if min_experience is not None:
            conditions.append(DoctorProfile.years_of_experience >= min_experience)
        if max_experience is not None:
            conditions.append(DoctorProfile.years_of_experience <= max_experience)

        if gender:
            conditions.append(DoctorProfile.gender == gender)

        # Fee and online filters need clinic join
        if min_fee is not None:
            conditions.append(DoctorClinic.consultation_fee >= min_fee)
        if max_fee is not None:
            conditions.append(DoctorClinic.consultation_fee <= max_fee)

        if online_consultation is not None:
            conditions.append(DoctorClinic.online_consultation == online_consultation)

        if city:
            conditions.append(sa_func.lower(DoctorClinic.city).like(f"%{city.lower()}%"))

        # Base query with joins
        stmt = (
            select(DoctorProfile)
            .join(User, DoctorProfile.user_id == User.id)
            .join(DoctorVerification, DoctorProfile.id == DoctorVerification.doctor_profile_id)
            .outerjoin(DoctorClinic, DoctorProfile.id == DoctorClinic.doctor_profile_id)
        )

        if availability_day:
            stmt = stmt.outerjoin(
                DoctorAvailability,
                and_(
                    DoctorClinic.id == DoctorAvailability.clinic_id,
                    DoctorAvailability.day_of_week == availability_day,
                    DoctorAvailability.is_active == True,
                ),
            )
            conditions.append(DoctorAvailability.id != None)

        stmt = stmt.where(and_(*conditions)).distinct()

        # Count query
        from sqlalchemy import func as sa_func2
        count_stmt = (
            select(sa_func2.count(DoctorProfile.id.distinct()))
            .select_from(DoctorProfile)
            .join(User, DoctorProfile.user_id == User.id)
            .join(DoctorVerification, DoctorProfile.id == DoctorVerification.doctor_profile_id)
            .outerjoin(DoctorClinic, DoctorProfile.id == DoctorClinic.doctor_profile_id)
        )
        if availability_day:
            count_stmt = count_stmt.outerjoin(
                DoctorAvailability,
                and_(
                    DoctorClinic.id == DoctorAvailability.clinic_id,
                    DoctorAvailability.day_of_week == availability_day,
                    DoctorAvailability.is_active == True,
                ),
            )
        count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Sorting
        if sort_by == "fee":
            stmt = stmt.order_by(DoctorClinic.consultation_fee.asc().nulls_last())
        elif sort_by == "name":
            stmt = stmt.order_by(User.full_name.asc())
        else:  # experience (default)
            stmt = stmt.order_by(DoctorProfile.years_of_experience.desc().nulls_last())

        stmt = stmt.offset(offset).limit(limit)

        # Eager-load relationships for the result set
        stmt = stmt.options(
            selectinload(DoctorProfile.qualifications),
            selectinload(DoctorProfile.specializations),
            selectinload(DoctorProfile.clinics).selectinload(DoctorClinic.availability_slots),
            selectinload(DoctorProfile.user),
        )

        result = await self.db.execute(stmt)
        profiles = list(result.scalars().unique().all())
        return profiles, total

    async def get_featured_doctors(self, limit: int = 8) -> list:
        """Top N approved doctors by experience for homepage."""
        from models.user import User

        stmt = (
            select(DoctorProfile)
            .join(User, DoctorProfile.user_id == User.id)
            .join(DoctorVerification, DoctorProfile.id == DoctorVerification.doctor_profile_id)
            .options(
                selectinload(DoctorProfile.qualifications),
                selectinload(DoctorProfile.specializations),
                selectinload(DoctorProfile.clinics).selectinload(DoctorClinic.availability_slots),
                selectinload(DoctorProfile.user),
            )
            .where(
                and_(
                    User.is_verified == True,
                    User.is_active == True,
                    DoctorProfile.is_profile_complete == True,
                    DoctorVerification.verification_status == VerificationStatus.APPROVED,
                )
            )
            .order_by(DoctorProfile.years_of_experience.desc().nulls_last())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_specialization_counts(self) -> list:
        """Count of approved doctors per specialization."""
        from models.user import User
        from sqlalchemy import func as sa_func

        stmt = (
            select(
                DoctorProfile.primary_specialization,
                sa_func.count(DoctorProfile.id.distinct()).label("count"),
            )
            .join(User, DoctorProfile.user_id == User.id)
            .join(DoctorVerification, DoctorProfile.id == DoctorVerification.doctor_profile_id)
            .where(
                and_(
                    User.is_verified == True,
                    User.is_active == True,
                    DoctorProfile.is_profile_complete == True,
                    DoctorVerification.verification_status == VerificationStatus.APPROVED,
                    DoctorProfile.primary_specialization != None,
                )
            )
            .group_by(DoctorProfile.primary_specialization)
            .order_by(sa_func.count(DoctorProfile.id.distinct()).desc())
        )
        result = await self.db.execute(stmt)
        return [{"name": row[0], "count": row[1]} for row in result.all()]

    async def get_top_clinics(self, limit: int = 6) -> list:
        """Top clinics with most verified doctors."""
        from models.user import User
        from sqlalchemy import func as sa_func

        stmt = (
            select(
                DoctorClinic.clinic_name,
                DoctorClinic.city,
                DoctorClinic.state,
                sa_func.count(DoctorProfile.id.distinct()).label("doctor_count"),
                sa_func.array_agg(DoctorProfile.primary_specialization.distinct()).label("specializations"),
            )
            .join(DoctorProfile, DoctorClinic.doctor_profile_id == DoctorProfile.id)
            .join(User, DoctorProfile.user_id == User.id)
            .join(DoctorVerification, DoctorProfile.id == DoctorVerification.doctor_profile_id)
            .where(
                and_(
                    User.is_verified == True,
                    User.is_active == True,
                    DoctorProfile.is_profile_complete == True,
                    DoctorVerification.verification_status == VerificationStatus.APPROVED,
                )
            )
            .group_by(DoctorClinic.clinic_name, DoctorClinic.city, DoctorClinic.state)
            .order_by(sa_func.count(DoctorProfile.id.distinct()).desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [
            {
                "clinic_name": row[0],
                "city": row[1],
                "state": row[2],
                "doctor_count": row[3],
                "specializations": [s for s in (row[4] or []) if s is not None],
            }
            for row in result.all()
        ]
