"""
Reviews API — Doctor ratings & comments by patients
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dependencies.auth import get_patient, get_current_user
from models.user import User
from services.review_service import ReviewService
from schemas.review import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", summary="Submit a doctor review (patient only)")
async def create_review(
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = ReviewService(db)
    review = await svc.create_review(payload, current_user)
    return {"message": "Review submitted.", "review_id": str(review.id)}


@router.put("/{review_id}", summary="Update your review")
async def update_review(
    review_id: UUID,
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = ReviewService(db)
    review = await svc.update_review(review_id, rating, comment, current_user)
    return {"message": "Review updated.", "review_id": str(review.id)}


@router.delete("/{review_id}", summary="Delete your review")
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = ReviewService(db)
    await svc.delete_review(review_id, current_user)
    return {"message": "Review deleted."}


@router.get("/doctor/{doctor_profile_id}", summary="Get all reviews for a doctor")
async def get_doctor_reviews(
    doctor_profile_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    svc = ReviewService(db)
    return await svc.get_doctor_reviews(doctor_profile_id)


@router.get("/my", summary="Get my submitted reviews")
async def get_my_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_patient),
):
    svc = ReviewService(db)
    reviews = await svc.get_my_reviews(current_user)
    return [
        {
            "id": str(r.id),
            "doctor_profile_id": str(r.doctor_profile_id),
            "rating": r.rating,
            "comment": r.comment,
            "is_anonymous": r.is_anonymous,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]
