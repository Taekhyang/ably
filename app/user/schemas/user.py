import re

from core.exceptions import UnprocessableEntity
from pydantic import (
    BaseModel,
    Field,
    validator,
    constr
)


def phone_number_format(val):
    pattern = r"[0-9]{10,11}"
    is_valid = True if re.fullmatch(pattern, val) else False
    if not is_valid:
        raise UnprocessableEntity("phone number format is not valid")
    return val


def email_format(val):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    is_valid = True if re.fullmatch(pattern, val) else False
    if not is_valid:
        raise UnprocessableEntity("email format is not valid")
    return val


class UserCommonValidator:
    @staticmethod
    def validate_phone(*args, **kwargs):
        decorator = validator(*args, **kwargs, allow_reuse=True)
        decorated = decorator(phone_number_format)
        return decorated

    @staticmethod
    def validate_email(*args, **kwargs):
        decorator = validator(*args, **kwargs, allow_reuse=True)
        decorated = decorator(email_format)
        return decorated


class PhoneDuplicateCheckRequestSchema(BaseModel):
    phone: str = Field(..., description="중복검사 대상 휴대폰 번호")

    _phone_number_format = UserCommonValidator.validate_phone("phone", pre=True)


class EmailDuplicateCheckRequestSchema(BaseModel):
    email: constr(max_length=255) = Field(..., description="중복검사 대상 이메일")

    _email_format = UserCommonValidator.validate_email("email", pre=True)


class SMSAuthSendRequestSchema(BaseModel):
    phone: str = Field(..., description="인증받을 휴대폰 번호")

    _phone_number_format = UserCommonValidator.validate_phone("phone", pre=True)


class AuthCodeVerificationRequestSchema(BaseModel):
    session_id: str = Field(..., description="Client Session ID")
    phone: str = Field(..., description="인증받을 휴대폰 번호")
    auth_code: constr(max_length=6) = Field(..., description="인증번호")

    _phone_number_format = UserCommonValidator.validate_phone("phone", pre=True)


class UserSignUpRequestSchema(BaseModel):
    name: constr(max_length=20) = Field(..., description="실명")
    nickname: constr(max_length=10) = Field(..., description="닉네임")
    email: constr(max_length=255) = Field(..., description="이메일")
    password: constr(min_length=8, max_length=30) = Field(..., description="8자리 이상 30자리 이하 비밀번호")
    session_id: str = Field(..., description="Client Session ID")

    _email_format = UserCommonValidator.validate_email("email", pre=True)


class UserProfileResponseSchema(BaseModel):
    id: int = Field(..., description="User ID")
    name: constr(max_length=30) = Field(..., description="실명")
    nickname: constr(max_length=20) = Field(..., description="닉네임")
    email: constr(max_length=255) = Field(..., description="이메일")
    phone: str = Field(..., description="휴대폰 번호")

    _email_format = UserCommonValidator.validate_email("email", pre=True)
    _phone_number_format = UserCommonValidator.validate_phone("phone", pre=True)
