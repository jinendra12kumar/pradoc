"""
Admin Service — Platform Management & Statistics
"""
from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, func, and_, cast, Numeric
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole
from models.doctor import DoctorProfile, DoctorVerification, VerificationStatus
from models.appointment import Appointment, AppointmentStatus, PatientProfile
from models.review import DoctorReview, ReviewStatus
from models.article import Article


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Stats ─────────────────────────────────────────────────────────────────
    async def get_stats(self) -> dict:
        today = date.today()

        total_doctors = await self.db.execute(
            select(func.count()).where(User.role == UserRole.doctor)
        )
        total_patients = await self.db.execute(
            select(func.count()).where(User.role == UserRole.patient)
        )
        today_appts = await self.db.execute(
            select(func.count()).where(Appointment.appointment_date == today)
        )
        revenue = await self.db.execute(
            select(func.coalesce(func.sum(Appointment.fee_charged), 0))
            .where(Appointment.status == AppointmentStatus.completed)
        )
        pending_verifications = await self.db.execute(
            select(func.count()).where(
                DoctorVerification.verification_status == VerificationStatus.PENDING
            )
        )
        total_articles = await self.db.execute(select(func.count(Article.id)))
        total_reviews  = await self.db.execute(select(func.count(DoctorReview.id)))

        # Status breakdown
        status_breakdown = {}
        for s in AppointmentStatus:
            cnt = await self.db.execute(
                select(func.count()).where(Appointment.status == s)
            )
            status_breakdown[s.value] = cnt.scalar() or 0

        return {
            "total_doctors": total_doctors.scalar() or 0,
            "total_patients": total_patients.scalar() or 0,
            "today_appointments": today_appts.scalar() or 0,
            "total_revenue": float(revenue.scalar() or 0),
            "pending_verifications": pending_verifications.scalar() or 0,
            "total_articles": total_articles.scalar() or 0,
            "total_reviews": total_reviews.scalar() or 0,
            "appointment_status_breakdown": status_breakdown,
        }

    # ── Doctors ───────────────────────────────────────────────────────────────
    async def list_doctors(self, page: int = 1, page_size: int = 20, search: str = "") -> dict:
        q = select(DoctorProfile)
        if search:
            user_ids_r = await self.db.execute(
                select(User.id).where(User.full_name.ilike(f"%{search}%"))
            )
            user_ids = [r for r in user_ids_r.scalars().all()]
            if user_ids:
                q = q.where(DoctorProfile.user_id.in_(user_ids))
            else:
                return {"total": 0, "page": page, "page_size": page_size, "items": []}

        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(
            q.order_by(DoctorProfile.created_at.desc())
             .offset((page - 1) * page_size).limit(page_size)
        )
        doctors = items_r.scalars().all()

        results = []
        for dp in doctors:
            user = await self.db.get(User, dp.user_id)
            verif = dp.verification
            results.append({
                "id": str(dp.id),
                "user_id": str(dp.user_id),
                "full_name": user.full_name if user else "Unknown",
                "email": user.email if user else "",
                "mobile": user.mobile if user else "",
                "primary_specialization": dp.primary_specialization,
                "years_of_experience": dp.years_of_experience,
                "is_profile_complete": dp.is_profile_complete,
                "profile_completion_pct": dp.profile_completion_pct,
                "verification_status": verif.verification_status.value if verif else "PENDING",
                "verification_score": verif.verification_score if verif else 0,
                "is_active": user.is_active if user else False,
                "created_at": dp.created_at.isoformat() if dp.created_at else None,
            })
        return {"total": total_r.scalar() or 0, "page": page, "page_size": page_size, "items": results}

    async def update_doctor_verification(self, doctor_profile_id: UUID, new_status: str, reason: str = None) -> dict:
        dp = await self.db.get(DoctorProfile, doctor_profile_id)
        if not dp:
            raise HTTPException(status_code=404, detail="Doctor profile not found.")
        verif = dp.verification
        if not verif:
            raise HTTPException(status_code=404, detail="Doctor verification record not found.")
        verif.verification_status = VerificationStatus(new_status)
        if reason:
            verif.rejection_reason = reason
        verif.reviewed_at = datetime.utcnow()
        await self.db.commit()
        return {"message": f"Doctor verification updated to {new_status}."}

    async def toggle_doctor_active(self, doctor_profile_id: UUID, is_active: bool) -> dict:
        dp = await self.db.get(DoctorProfile, doctor_profile_id)
        if not dp:
            raise HTTPException(status_code=404, detail="Doctor not found.")
        user = await self.db.get(User, dp.user_id)
        if user:
            user.is_active = is_active
            await self.db.commit()
        return {"message": f"Doctor {'activated' if is_active else 'deactivated'}."}

    # ── Patients ──────────────────────────────────────────────────────────────
    async def list_patients(self, page: int = 1, page_size: int = 20, search: str = "") -> dict:
        q = select(User).where(User.role == UserRole.patient)
        if search:
            q = q.where(User.full_name.ilike(f"%{search}%"))
        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(
            q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        users = items_r.scalars().all()

        results = []
        for u in users:
            pp_r = await self.db.execute(
                select(PatientProfile).where(PatientProfile.user_id == u.id)
            )
            pp = pp_r.scalar_one_or_none()
            appt_count_r = await self.db.execute(
                select(func.count()).where(Appointment.patient_id == pp.id) if pp else select(func.count()).where(False)
            )
            results.append({
                "id": str(u.id),
                "full_name": u.full_name,
                "email": u.email,
                "mobile": u.mobile,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "appointment_count": appt_count_r.scalar() or 0,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            })
        return {"total": total_r.scalar() or 0, "page": page, "page_size": page_size, "items": results}

    async def toggle_patient_active(self, user_id: UUID, is_active: bool) -> dict:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        user.is_active = is_active
        await self.db.commit()
        return {"message": f"Patient {'activated' if is_active else 'deactivated'}."}

    # ── Appointments ──────────────────────────────────────────────────────────
    async def list_appointments(
        self, page: int = 1, page_size: int = 20,
        status_filter: Optional[str] = None, date_filter: Optional[str] = None
    ) -> dict:
        q = select(Appointment)
        if status_filter:
            q = q.where(Appointment.status == AppointmentStatus(status_filter))
        if date_filter == "today":
            q = q.where(Appointment.appointment_date == date.today())
        elif date_filter == "upcoming":
            q = q.where(Appointment.appointment_date >= date.today())
        elif date_filter == "past":
            q = q.where(Appointment.appointment_date < date.today())

        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(
            q.order_by(Appointment.appointment_date.desc(), Appointment.slot_start_time)
             .offset((page - 1) * page_size).limit(page_size)
        )
        appts = items_r.scalars().all()

        results = []
        for a in appts:
            pp = await self.db.get(PatientProfile, a.patient_id)
            dp = await self.db.get(DoctorProfile, a.doctor_profile_id)
            patient_user = await self.db.get(User, pp.user_id) if pp else None
            doctor_user  = await self.db.get(User, dp.user_id) if dp else None
            results.append({
                "id": str(a.id),
                "patient_name": patient_user.full_name if patient_user else "Unknown",
                "doctor_name": f"Dr. {doctor_user.full_name}" if doctor_user else "Unknown",
                "appointment_date": str(a.appointment_date),
                "slot_start_time": str(a.slot_start_time),
                "consultation_type": a.consultation_type.value,
                "status": a.status.value,
                "fee_charged": float(a.fee_charged) if a.fee_charged else 0,
                "meeting_started_at": a.meeting_started_at.isoformat() if a.meeting_started_at else None,
                "booked_at": a.booked_at.isoformat() if a.booked_at else None,
            })
        return {"total": total_r.scalar() or 0, "page": page, "page_size": page_size, "items": results}

    async def update_appointment_status(self, appointment_id: UUID, new_status: str) -> dict:
        appt = await self.db.get(Appointment, appointment_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found.")
        appt.status = AppointmentStatus(new_status)
        await self.db.commit()
        return {"message": f"Appointment status updated to {new_status}."}

    # ── Reviews ───────────────────────────────────────────────────────────────
    async def list_reviews(self, page: int = 1, page_size: int = 20) -> dict:
        q = select(DoctorReview)
        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(
            q.order_by(DoctorReview.created_at.desc())
             .offset((page - 1) * page_size).limit(page_size)
        )
        reviews = items_r.scalars().all()

        results = []
        for rv in reviews:
            pp = await self.db.get(PatientProfile, rv.patient_id)
            dp = await self.db.get(DoctorProfile, rv.doctor_profile_id)
            patient_user = await self.db.get(User, pp.user_id) if pp else None
            doctor_user  = await self.db.get(User, dp.user_id) if dp else None
            results.append({
                "id": str(rv.id),
                "patient_name": patient_user.full_name if patient_user else "Anonymous",
                "doctor_name": f"Dr. {doctor_user.full_name}" if doctor_user else "Unknown",
                "rating": rv.rating,
                "comment": rv.comment,
                "is_anonymous": rv.is_anonymous,
                "status": rv.status.value,
                "created_at": rv.created_at.isoformat() if rv.created_at else None,
            })
        return {"total": total_r.scalar() or 0, "page": page, "page_size": page_size, "items": results}

    async def delete_review(self, review_id: UUID) -> dict:
        rv = await self.db.get(DoctorReview, review_id)
        if not rv:
            raise HTTPException(status_code=404, detail="Review not found.")
        await self.db.delete(rv)
        await self.db.commit()
        return {"message": "Review deleted."}

    async def update_review_status(self, review_id: UUID, new_status: str) -> dict:
        rv = await self.db.get(DoctorReview, review_id)
        if not rv:
            raise HTTPException(status_code=404, detail="Review not found.")
        rv.status = ReviewStatus(new_status)
        await self.db.commit()
        return {"message": f"Review status updated to {new_status}."}

    # ── Articles ──────────────────────────────────────────────────────────────
    @staticmethod
    def _make_slug(title: str) -> str:
        slug = title.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = slug[:200] + "-" + str(uuid.uuid4())[:8]
        return slug

    async def list_articles(self, page: int = 1, page_size: int = 20, published_only: bool = False) -> dict:
        q = select(Article)
        if published_only:
            q = q.where(Article.is_published == True)
        total_r = await self.db.execute(select(func.count()).select_from(q.subquery()))
        items_r = await self.db.execute(
            q.order_by(Article.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        articles = items_r.scalars().all()
        return {
            "total": total_r.scalar() or 0, "page": page, "page_size": page_size,
            "items": [
                {
                    "id": str(a.id), "title": a.title, "slug": a.slug, "excerpt": a.excerpt,
                    "category": a.category, "author_name": a.author_name,
                    "cover_image_url": a.cover_image_url, "is_published": a.is_published,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in articles
            ]
        }

    async def create_article(self, payload: dict) -> dict:
        article = Article(
            title=payload["title"],
            slug=self._make_slug(payload["title"]),
            excerpt=payload.get("excerpt"),
            content=payload["content"],
            category=payload.get("category"),
            author_name=payload.get("author_name", "PraDoc Team"),
            cover_image_url=payload.get("cover_image_url"),
            is_published=payload.get("is_published", False),
            published_at=datetime.utcnow() if payload.get("is_published") else None,
        )
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        return {"message": "Article created.", "id": str(article.id), "slug": article.slug}

    async def update_article(self, article_id: UUID, payload: dict) -> dict:
        article = await self.db.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found.")
        for field in ["title", "excerpt", "content", "category", "author_name", "cover_image_url"]:
            if field in payload:
                setattr(article, field, payload[field])
        if "is_published" in payload:
            was_published = article.is_published
            article.is_published = payload["is_published"]
            if payload["is_published"] and not was_published:
                article.published_at = datetime.utcnow()
        await self.db.commit()
        return {"message": "Article updated."}

    async def delete_article(self, article_id: UUID) -> dict:
        article = await self.db.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found.")
        await self.db.delete(article)
        await self.db.commit()
        return {"message": "Article deleted."}

    async def get_article(self, article_id: UUID) -> dict:
        article = await self.db.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found.")
        return {
            "id": str(article.id), "title": article.title, "slug": article.slug,
            "excerpt": article.excerpt, "content": article.content,
            "category": article.category, "author_name": article.author_name,
            "cover_image_url": article.cover_image_url, "is_published": article.is_published,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "created_at": article.created_at.isoformat() if article.created_at else None,
        }
