"""
Admin User Seed Script
Usage:
    cd backend
    python utils/admin_seed.py

This creates an admin user directly in the DB.
Edit the variables below before running.
"""
import asyncio
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal, create_tables
from core.security import hash_password
from repositories.user_repo import UserRepository
from models.user import UserRole

# ── Configure admin credentials here ─────────────────────────────────────────
ADMIN_FULL_NAME  = "Super Admin"
ADMIN_EMAIL      = "admin@pradoc.health"
ADMIN_MOBILE     = "9000000000"
ADMIN_PASSWORD   = "Admin@1234"   # Change before running!
# ─────────────────────────────────────────────────────────────────────────────


async def seed_admin():
    await create_tables()
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)

        existing = await repo.get_by_email(ADMIN_EMAIL)
        if existing:
            print(f"[INFO] Admin already exists: {ADMIN_EMAIL}")
            return

        user = await repo.create(
            full_name=ADMIN_FULL_NAME,
            email=ADMIN_EMAIL,
            mobile=ADMIN_MOBILE,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        # Admin is pre-verified
        user.is_verified = True
        db.add(user)
        await db.commit()
        print(f"[SUCCESS] Admin user created: {ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed_admin())
