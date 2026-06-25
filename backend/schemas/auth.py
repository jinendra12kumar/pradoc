import re
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from models.user import UserRole


# ── Register ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    password: str
    confirm_password: str
    role: UserRole = UserRole.patient

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        v = re.sub(r"[\s\-\(\)\+]", "", v)
        # Accept 10-digit Indian numbers or with 91 prefix
        if re.match(r"^91[6-9]\d{9}$", v):
            v = v[2:]
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Enter a valid 10-digit Indian mobile number")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must have at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must have at least one digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class RegisterResponse(BaseModel):
    message: str
    email: str


# ── OTP ───────────────────────────────────────────────────────────────────────

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be exactly 6 digits")
        return v


class ResendOTPRequest(BaseModel):
    email: EmailStr


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    identifier: str   # email or mobile number
    password: str


# ── Tokens ────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    mobile: str
    role: str
    is_verified: bool
    is_active: bool

    model_config = {"from_attributes": True}
