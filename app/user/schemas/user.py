import re

from pydantic import BaseModel, Field, validator, constr


class AuthCodeVerificationRequestSchema(BaseModel):
    session_id: str = Field(..., description="Client Session ID")
    phone: str = Field(..., description="인증받을 휴대폰 번호")
    auth_code: constr(max_length=6) = Field(..., description="인증번호")


class UserSignUpRequestSchema(BaseModel):
    name: constr(max_length=20) = Field(..., description="실명")
    nickname: constr(max_length=10) = Field(..., description="닉네임")
    email: constr(max_length=255) = Field(..., description="이메일")
    phone: str = Field(..., description="휴대폰 번호")
    password: constr(min_length=8, max_length=30) = Field(..., description="8자리 이상 30자리 이하 비밀번호")
    session_id: str = Field(..., description="Client Session ID")

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
    name: constr(max_length=30) = Field(..., description="실명")
    nickname: constr(max_length=20) = Field(..., description="닉네임")
    email: constr(max_length=255) = Field(..., description="이메일")
    phone: str = Field(..., description="휴대폰 번호")
