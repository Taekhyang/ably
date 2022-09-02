import random
import datetime as dt

from fastapi import APIRouter, Depends, Query, Request

from app.user.schemas import *
from app.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated
)
from core.utils.logger import debugger
from core.utils.token_helper import TokenHelper
from core.utils.session_generator import generate_random_session_id
from core.utils.sms_sender import send_sms
from core.exceptions import SMSSenderException, NotFoundException


user_router = APIRouter()


@user_router.get(
    "/profile",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
async def get_user_profile(request: Request):
    pass


@user_router.get(
    "/email/duplicate-check"
)
async def check_duplicate_email(email: str = Query(..., description="중복검사 대상 이메일")):
    user = await UserService().get_user_by_email(email)
    if user:
        return {"is_duplicated": True}
    return {"is_duplicated": False}


@user_router.get(
    "/phone/duplicate-check"
)
async def check_duplicate_email(phone: str = Query(..., description="중복검사 대상 휴대폰 번호")):
    user = await UserService().get_user_by_phone(phone)
    if user:
        return {"is_duplicated": True}
    return {"is_duplicated": False}


@user_router.get(
    "/sms-auth/send"
)
async def send_sms_auth_code(phone: str = Query(..., description="인증받을 휴대폰 번호")):
    session_id = generate_random_session_id()
    auth_code = str(random.randint(100000, 999999))

    is_success = send_sms(phone, auth_code)
    if is_success:
        await UserService().create_temp_sms_auth(
            session_id,
            phone,
            auth_code,
            dt.datetime.now()
        )
        return {"session_id": session_id}
    raise SMSSenderException


@user_router.post(
    "/sms-auth/verify"
)
async def verify_sms_auth_code(request: AuthCodeVerificationRequestSchema):
    temp_sms_auth = await UserService().get_temp_sms_auth(request.session_id)
    if not temp_sms_auth:
        raise NotFoundException

    if temp_sms_auth.auth_code == request.auth_code and temp_sms_auth.phone == request.phone:
        await UserService().set_verified_flag(request.session_id)
        return {"is_verified": True}
    return {"is_verified": False}
