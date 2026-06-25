import random
import string
from core.redis_client import get_redis
from core.config import settings

_OTP_PREFIX = "otp:"
_ATTEMPTS_PREFIX = "otp_attempts:"


async def generate_and_store_otp(email: str) -> str:
    """Generate 6-digit OTP, persist to Redis with TTL."""
    otp = "".join(random.choices(string.digits, k=6))
    redis = await get_redis()
    await redis.set(f"{_OTP_PREFIX}{email}", otp, ex=settings.OTP_EXPIRE_SECONDS)
    await redis.set(f"{_ATTEMPTS_PREFIX}{email}", "0", ex=settings.OTP_EXPIRE_SECONDS)
    return otp


async def verify_otp(email: str, otp: str) -> bool:
    """
    Validate OTP against Redis store.
    Raises ValueError on failure; returns True on success.
    """
    redis = await get_redis()
    otp_key = f"{_OTP_PREFIX}{email}"
    attempts_key = f"{_ATTEMPTS_PREFIX}{email}"

    attempts_raw = await redis.get(attempts_key)
    attempts = int(attempts_raw or 0)

    if attempts >= settings.OTP_MAX_ATTEMPTS:
        raise ValueError("Too many failed attempts. Please request a new OTP.")

    stored = await redis.get(otp_key)
    if not stored:
        raise ValueError("OTP has expired. Please request a new one.")

    if stored != otp:
        new_attempts = attempts + 1
        await redis.set(attempts_key, str(new_attempts), ex=settings.OTP_EXPIRE_SECONDS)
        remaining = settings.OTP_MAX_ATTEMPTS - new_attempts
        if remaining <= 0:
            raise ValueError("Too many failed attempts. Please request a new OTP.")
        raise ValueError(f"Invalid OTP. {remaining} attempt(s) remaining.")

    # Valid — clean up Redis
    await redis.delete(otp_key)
    await redis.delete(attempts_key)
    return True


async def invalidate_otp(email: str) -> None:
    """Remove OTP and attempts from Redis (e.g. on resend)."""
    redis = await get_redis()
    await redis.delete(f"{_OTP_PREFIX}{email}")
    await redis.delete(f"{_ATTEMPTS_PREFIX}{email}")
