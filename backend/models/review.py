"""
Doctor Reviews & Ratings — SQLAlchemy Model
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Integer,
    Enum as SAEnum, ForeignKey, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class ReviewStatus(str, enum.Enum):
    active   = "active"
    hidden   = "hidden"    # Admin can hide abusive reviews
    reported = "reported"


class DoctorReview(Base):
    __tablename__ = "doctor_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Who reviewed whom
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
    appointment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Rating (1–5)
    rating  = Column(Integer, nullable=False)   # 1 to 5
    comment = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)

    # Moderation
    status = Column(
        SAEnum(ReviewStatus, name="review_status_enum", create_type=True),
        default=ReviewStatus.active,
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    doctor  = relationship("DoctorProfile", backref="reviews")
    patient = relationship("PatientProfile", backref="reviews")

    # One review per patient per doctor
    __table_args__ = (
        UniqueConstraint("doctor_profile_id", "patient_id", name="uq_patient_doctor_review"),
    )

    def __repr__(self) -> str:
        return f"<DoctorReview rating={self.rating} doctor={self.doctor_profile_id}>"
