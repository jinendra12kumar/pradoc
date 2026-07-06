"""
Video Consultation — API Router
Embedded Jitsi Meet (no redirect); HTTP-safe for local development.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dependencies.auth import get_current_user, get_doctor, get_any_user
from models.user import User
from services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video Consultation"])


@router.post(
    "/create-meeting/{appointment_id}",
    summary="Doctor creates/starts a video meeting room",
)
async def create_meeting(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    """
    Called by the doctor to open the Jitsi room.
    Sets `meeting_started_at` on the appointment.
    Returns room_name and display info for the Jitsi External API embed.
    """
    svc = VideoService(db)
    return await svc.create_meeting(appointment_id, current_user)


@router.get(
    "/join/{appointment_id}",
    summary="Get join info for a video meeting (doctor or patient)",
)
async def get_join_info(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_any_user),
):
    """
    Returns room_name, display_name, is_host and meeting_started flag.
    Patients use `meeting_started` to know when to leave the waiting room.
    """
    svc = VideoService(db)
    return await svc.get_join_info(appointment_id, current_user)


@router.post(
    "/end-meeting/{appointment_id}",
    summary="Doctor ends the video meeting and completes appointment",
)
async def end_meeting(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_doctor),
):
    """
    Sets `meeting_ended_at`, transitions appointment status → completed.
    """
    svc = VideoService(db)
    return await svc.end_meeting(appointment_id, current_user)
