"""
Admin — API Router (admin role only)
Manages Doctors, Patients, Appointments, Articles, Reviews & Platform Stats
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dependencies.auth import get_admin
from models.user import User
from services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


# ═══════════════════════════════════════════════════════════════════════════════
# STATS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats", summary="Platform statistics for admin dashboard")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.get_stats()


# ═══════════════════════════════════════════════════════════════════════════════
# DOCTORS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/doctors", summary="List all doctors")
async def list_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.list_doctors(page, page_size, search)


@router.put("/doctors/{doctor_profile_id}/verify", summary="Approve or reject doctor verification")
async def update_doctor_verification(
    doctor_profile_id: UUID,
    status: str = Query(..., description="APPROVED | REJECTED | SUSPENDED | UNDER_REVIEW"),
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.update_doctor_verification(doctor_profile_id, status, reason)


@router.put("/doctors/{doctor_profile_id}/toggle-active", summary="Enable or disable doctor account")
async def toggle_doctor_active(
    doctor_profile_id: UUID,
    is_active: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.toggle_doctor_active(doctor_profile_id, is_active)


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/patients", summary="List all patients")
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.list_patients(page, page_size, search)


@router.put("/patients/{user_id}/toggle-active", summary="Enable or disable patient account")
async def toggle_patient_active(
    user_id: UUID,
    is_active: bool = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.toggle_patient_active(user_id, is_active)


# ═══════════════════════════════════════════════════════════════════════════════
# APPOINTMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/appointments", summary="List all appointments with filters")
async def list_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    date_filter: Optional[str] = Query(None, description="today|upcoming|past"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.list_appointments(page, page_size, status, date_filter)


@router.put("/appointments/{appointment_id}/status", summary="Override appointment status")
async def update_appointment_status(
    appointment_id: UUID,
    status: str = Query(..., description="pending|confirmed|completed|cancelled|no_show"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.update_appointment_status(appointment_id, status)


# ═══════════════════════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/reviews", summary="List all reviews")
async def list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.list_reviews(page, page_size)


@router.delete("/reviews/{review_id}", summary="Delete a review")
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.delete_review(review_id)


@router.put("/reviews/{review_id}/status", summary="Update review moderation status")
async def update_review_status(
    review_id: UUID,
    status: str = Query(..., description="active|hidden|reported"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.update_review_status(review_id, status)


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLES
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/articles", summary="List all articles")
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    published_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.list_articles(page, page_size, published_only)


@router.get("/articles/{article_id}", summary="Get a single article by ID")
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.get_article(article_id)


@router.post("/articles", summary="Create a new article")
async def create_article(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.create_article(payload)


@router.put("/articles/{article_id}", summary="Update an existing article")
async def update_article(
    article_id: UUID,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.update_article(article_id, payload)


@router.delete("/articles/{article_id}", summary="Delete an article")
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin),
):
    svc = AdminService(db)
    return await svc.delete_article(article_id)


# ── Public: patients can read published articles ──────────────────────────────
@router.get("/articles-public", summary="Public: list published articles", tags=["Public"])
async def list_published_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    svc = AdminService(db)
    return await svc.list_articles(page, page_size, published_only=True)
