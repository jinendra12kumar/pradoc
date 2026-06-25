from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from models.user import User, UserRole


class UserRepository:
    """Data-access layer for the User model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Readers ───────────────────────────────────────────────────────────────

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_mobile(self, mobile: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.mobile == mobile))
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Find user by email OR mobile number."""
        result = await self.db.execute(
            select(User).where(
                or_(User.email == identifier, User.mobile == identifier)
            )
        )
        return result.scalar_one_or_none()

    # ── Writers ───────────────────────────────────────────────────────────────

    async def create(
        self,
        full_name: str,
        email: str,
        mobile: str,
        hashed_password: str,
        role: UserRole,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            mobile=mobile,
            hashed_password=hashed_password,
            role=role,
            is_verified=False,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def mark_verified(self, user: User) -> User:
        user.is_verified = True
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
