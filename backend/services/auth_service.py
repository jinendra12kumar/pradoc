from fastapi import HTTPException, status,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repo import UserRepository
from services.otp_service import generate_and_store_otp, verify_otp, invalidate_otp
from core.security import hash_password, verify_password, build_token_pair, decode_token
from models.user import UserRole
from schemas.auth import RegisterRequest, LoginRequest, OTPVerifyRequest
#from tasks.email_tasks import send_otp_email
from services.email_service import send_otp_email_sync

class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    # ── Register ──────────────────────────────────────────────────────────────
    async def register(self, data: RegisterRequest,background_tasks: BackgroundTasks) -> dict:
        # Duplicate checks
        existing_user = await self.repo.get_by_email(data.email)

        if existing_user:

            # Already verified → block registration
            if existing_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists.",
                )

            # Not verified → resend OTP
            await invalidate_otp(data.email)
            otp = await generate_and_store_otp(data.email)

            background_tasks.add_task(
                send_otp_email_sync,
                email=existing_user.email,
                full_name=existing_user.full_name,
                otp=otp,
                role=existing_user.role.value,
            )

            return {
                "message": "Account already exists but is not verified. New OTP sent.",
                "email": existing_user.email,
            }
        existing_mobile = await self.repo.get_by_mobile(data.mobile)

        if existing_mobile and existing_mobile.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this mobile number already exists.",
            )

        # Prevent self-registration as admin
        if data.role == UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin accounts cannot be self-registered.",
            )

        # Create unverified user
        user = await self.repo.create(
            full_name=data.full_name,
            email=data.email,
            mobile=data.mobile,
            hashed_password=hash_password(data.password),
            role=data.role,
        )

        # Generate OTP and dispatch email via Celery
        otp = await generate_and_store_otp(data.email)

        background_tasks.add_task(
            send_otp_email_sync,
            email=user.email,
            full_name=user.full_name,
            otp=otp,
            role=user.role.value,
        )

        return {"message": "OTP sent to your email. Please verify.", "email": data.email}



    
    # async def register(self, data: RegisterRequest) -> dict:
    #     # Duplicate checks
    #     if await self.repo.get_by_email(data.email):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="An account with this email already exists.",
    #         )
    #     if await self.repo.get_by_mobile(data.mobile):
    #         raise HTTPException(
    #             status_code=status.HTTP_409_CONFLICT,
    #             detail="An account with this mobile number already exists.",
    #         )

    #     # Prevent self-registration as admin
    #     if data.role == UserRole.admin:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Admin accounts cannot be self-registered.",
    #         )

    #     # Create unverified user
    #     user = await self.repo.create(
    #         full_name=data.full_name,
    #         email=data.email,
    #         mobile=data.mobile,
    #         hashed_password=hash_password(data.password),
    #         role=data.role,
    #     )

    #     # Generate OTP and dispatch email via Celery
    #     otp = await generate_and_store_otp(data.email)
    #     send_otp_email.delay(
    #         email=data.email,
    #         full_name=data.full_name,
    #         otp=otp,
    #         role=data.role.value,
    #     )

    #     return {"message": "OTP sent to your email. Please verify.", "email": data.email}

    # ── Verify OTP ────────────────────────────────────────────────────────────

    async def verify_otp(self, data: OTPVerifyRequest) -> dict:
        user = await self.repo.get_by_email(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
            )

        try:
            await verify_otp(data.email, data.otp)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        user = await self.repo.mark_verified(user)
        return build_token_pair(str(user.id), user.email, user.role.value)

    # ── Resend OTP ────────────────────────────────────────────────────────────

    async def resend_otp(self, email: str,background_tasks: BackgroundTasks) -> dict:
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
            )

        await invalidate_otp(email)
        otp = await generate_and_store_otp(email)

        background_tasks.add_task(
            send_otp_email_sync,
            email=user.email,
            full_name=user.full_name,
            otp=otp,
            role=user.role.value,
        )
        return {"message": "A new OTP has been sent to your email.", "email": email}

    # ── Login ─────────────────────────────────────────────────────────────────

    async def login(self, data: LoginRequest) -> dict:
        user = await self.repo.get_by_identifier(data.identifier)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated.",
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in.",
            )
        return build_token_pair(str(user.id), user.email, user.role.value)

    # ── Refresh Token ─────────────────────────────────────────────────────────

    async def refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type.",
            )

        user = await self.repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        return build_token_pair(str(user.id), user.email, user.role.value)
