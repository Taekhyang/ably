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
from core.exceptions import SMSSenderException


user_router = APIRouter()


@user_router.post(
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
