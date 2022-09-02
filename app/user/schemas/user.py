import re

from pydantic import BaseModel, Field, validator


class DuplicateEmailCheckRequestSchema(BaseModel):
    email: str = Field(..., description="이메일", lte=255)


class DuplicatePhoneCheckRequestSchema(BaseModel):
    phone: str = Field(..., description="휴대폰 번호")


class SMSAuthCodeRequestSchema(BaseModel):
    phone: str = Field(..., description="인증받을 휴대폰 번호")


class SMSAuthCodeResponseSchema(BaseModel):
    session_id: str = Field(..., description="Client Session ID")


class AuthCodeValidationRequestSchema(BaseModel):
    session_id: str = Field(..., description="Client Session ID")
    phone: str = Field(..., description="인증받을 휴대폰 번호")
    auth_code: str = Field(..., description="인증번호", le=6)


class UserSignUpRequestSchema(BaseModel):
    name: str = Field(..., description="실명", le=20)
    nickname: str = Field(..., description="닉네임", le=10)
    email: str = Field(..., description="이메일", le=255)
    phone: str = Field(..., description="휴대폰 번호")
    password: str = Field(..., description="8자리 이상 30자리 이하 비밀번호", ge=8, le=30)

    class Config:
        orm_mode = True

    @validator("email")
    def email_format(cls, val):
        pattern = r"[^@]+@[^@]+\.[^@]+"
        is_valid = True if re.fullmatch(pattern, val) else False
        if not is_valid:
            raise ValueError("email format is not valid")
        return val

    @validator("phone")
    def phone_number_format(cls, val):
        pattern = r"[0-9]{10,11}"
        is_valid = True if re.fullmatch(pattern, val) else False
        if not is_valid:
            raise ValueError("phone number format is not valid")
        return val


class UserProfileResponseSchema(BaseModel):
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="실명", le=20)
    nickname: str = Field(..., description="닉네임", le=10)
    email: str = Field(..., description="이메일", le=255)
    phone: str = Field(..., description="휴대폰 번호")
