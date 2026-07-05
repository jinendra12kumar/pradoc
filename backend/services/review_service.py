"""
Review Service — Doctor rating & comments
"""
from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import DoctorReview, ReviewStatus
from models.appointment import PatientProfile, Appointment, AppointmentStatus
from models.user import User
from schemas.review import ReviewCreate


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_patient(self, user: User) -> PatientProfile:
        r = await self.db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user.id)
        )
        patient = r.scalar_one_or_none()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found.")
        return patient

    async def create_review(self, payload: ReviewCreate, user: User) -> DoctorReview:
        patient = await self._get_patient(user)

        # Check no duplicate review
        existing = await self.db.execute(
            select(DoctorReview).where(
                DoctorReview.doctor_profile_id == payload.doctor_profile_id,
                DoctorReview.patient_id == patient.id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this doctor. You can update your existing review.",
            )

        # Verify patient had a completed appointment with this doctor
        if payload.appointment_id:
            appt = await self.db.get(Appointment, payload.appointment_id)
            if not appt or appt.patient_id != patient.id:
                raise HTTPException(status_code=403, detail="Invalid appointment reference.")
        else:
            # Check at least one completed appointment exists
            completed = await self.db.execute(
                select(Appointment).where(
                    Appointment.patient_id == patient.id,
                    Appointment.doctor_profile_id == payload.doctor_profile_id,
                    Appointment.status == AppointmentStatus.completed,
                ).limit(1)
            )
            if not completed.scalar_one_or_none():
                raise HTTPException(
                    status_code=403,
                    detail="You can only review doctors after a completed appointment.",
                )

        review = DoctorReview(
            doctor_profile_id=payload.doctor_profile_id,
            patient_id=patient.id,
            appointment_id=payload.appointment_id,
            rating=payload.rating,
            comment=payload.comment,
            is_anonymous=payload.is_anonymous,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def update_review(
        self, review_id: UUID, rating: int, comment: Optional[str], user: User
    ) -> DoctorReview:
        patient = await self._get_patient(user)
        review = await self.db.get(DoctorReview, review_id)
        if not review or review.patient_id != patient.id:
            raise HTTPException(status_code=404, detail="Review not found.")
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be 1–5.")
        review.rating  = rating
        review.comment = comment
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete_review(self, review_id: UUID, user: User) -> None:
        patient = await self._get_patient(user)
        review = await self.db.get(DoctorReview, review_id)
        if not review or review.patient_id != patient.id:
            raise HTTPException(status_code=404, detail="Review not found.")
        await self.db.delete(review)
        await self.db.commit()

    async def get_doctor_reviews(self, doctor_profile_id: UUID) -> dict:
        """Return rating summary + recent reviews for a doctor."""
        r = await self.db.execute(
            select(DoctorReview).where(
                DoctorReview.doctor_profile_id == doctor_profile_id,
                DoctorReview.status == ReviewStatus.active,
            ).order_by(DoctorReview.created_at.desc())
        )
        reviews = r.scalars().all()

        if not reviews:
            return {
                "doctor_profile_id": str(doctor_profile_id),
                "average_rating": 0.0,
                "total_reviews": 0,
                "rating_breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "reviews": [],
            }

        total   = len(reviews)
        avg     = round(sum(rv.rating for rv in reviews) / total, 1)
        breakdown = {i: sum(1 for rv in reviews if rv.rating == i) for i in range(1, 6)}

        # Enrich with patient names
        enriched = []
        for rv in reviews:
            patient_name = None
            if not rv.is_anonymous:
                p = await self.db.get(PatientProfile, rv.patient_id)
                if p and p.user:
                    patient_name = p.user.full_name
            enriched.append({
                "id":                str(rv.id),
                "doctor_profile_id": str(rv.doctor_profile_id),
                "rating":            rv.rating,
                "comment":           rv.comment,
                "is_anonymous":      rv.is_anonymous,
                "patient_name":      patient_name,
                "created_at":        rv.created_at.isoformat(),
            })

        return {
            "doctor_profile_id": str(doctor_profile_id),
            "average_rating":    avg,
            "total_reviews":     total,
            "rating_breakdown":  breakdown,
            "reviews":           enriched,
        }

    async def get_my_reviews(self, user: User) -> list:
        patient = await self._get_patient(user)
        r = await self.db.execute(
            select(DoctorReview).where(DoctorReview.patient_id == patient.id)
            .order_by(DoctorReview.created_at.desc())
        )
        return r.scalars().all()
