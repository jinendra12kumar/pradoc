"""
Doctor Reviews — Pydantic v2 Schemas
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    doctor_profile_id: UUID
    appointment_id: Optional[UUID] = None
    rating: int
    comment: Optional[str] = None
    is_anonymous: bool = False

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        return v


class ReviewResponse(BaseModel):
    id: UUID
    doctor_profile_id: UUID
    rating: int
    comment: Optional[str]
    is_anonymous: bool
    patient_name: Optional[str]   # None if anonymous
    created_at: datetime
    model_config = {"from_attributes": True}


class DoctorRatingSummary(BaseModel):
    doctor_profile_id: UUID
    average_rating: float
    total_reviews: int
    rating_breakdown: dict   # {1: count, 2: count, ..., 5: count}
    reviews: List[ReviewResponse]
