from fastapi import APIRouter, Depends, status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    OTPVerifyRequest,
    ResendOTPRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from services.auth_service import AuthService
from dependencies.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Patient or Doctor",
)
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    return await svc.register(data,background_tasks)


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="Verify email OTP and activate account",
)
async def verify_otp(
    data: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    return await svc.verify_otp(data)


@router.post(
    "/resend-otp",
    summary="Resend OTP to registered email",
)
async def resend_otp(
    data: ResendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    return await svc.resend_otp(data.email,background_tasks)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email/mobile + password",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    return await svc.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    return await svc.refresh_token(data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        mobile=current_user.mobile,
        role=current_user.role.value,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
    )
