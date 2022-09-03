import random
import datetime as dt
import bcrypt

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Request
)

from app.user.schemas import *
from app.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated
)
from core.fastapi.background_tasks import cleanup_temp_sms_auth
from core.utils.logger import debugger
from core.utils.token_helper import TokenHelper
from core.utils.session_generator import generate_random_session_id
from core.utils.sms_sender import send_sms
from core.config import config
from core.exceptions import *


user_router = APIRouter()


@user_router.get(
    "/email/duplicate-check"
)
async def check_duplicate_email(request: EmailDuplicateCheckRequestSchema = Depends()):
    user = await UserService().get_user_by_email(request.email)
    if user:
        return {"is_duplicated": True}
    return {"is_duplicated": False}


@user_router.get(
    "/phone/duplicate-check"
)
async def check_duplicate_email(request: PhoneDuplicateCheckRequestSchema = Depends()):
    user = await UserService().get_user_by_phone(request.phone)
    if user:
        return {"is_duplicated": True}
    return {"is_duplicated": False}


@user_router.get(
    "/sms-auth/send"
)
async def send_sms_auth_code(request: SMSAuthSendRequestSchema = Depends()):
    session_id = generate_random_session_id()
    auth_code = str(random.randint(100000, 999999))
    debugger.debug(f"Auth code : {auth_code}")

    is_success = send_sms(request.phone, auth_code)
    if is_success:
        await UserService().create_temp_sms_auth(
            session_id,
            request.phone,
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
        raise NotFoundException(message="session_id not found")

    if temp_sms_auth.auth_code == request.auth_code and temp_sms_auth.phone == request.phone:
        if temp_sms_auth.code_sent_at + dt.timedelta(seconds=config.AUTH_CODE_EXPIRE_SECONDS) < dt.datetime.now():
            raise SMSAuthTimeoutException

        await UserService().set_verified_flag(request.session_id)
        return {"is_verified": True}
    raise SMSAuthCodeNotMatchedException


@user_router.post(
    "/signup"
)
async def signup_user(request: UserSignUpRequestSchema, background_tasks: BackgroundTasks):
    temp_sms_auth = await UserService().get_temp_sms_auth(request.session_id)
    if not temp_sms_auth:
        raise NotFoundException(message="session_id not found")

    if not temp_sms_auth.is_verified:
        raise UnauthorizedException(message="phone number not verified")

    existing_user = await UserService().get_user_by_phone(temp_sms_auth.phone)
    if existing_user:
        raise DuplicateUserException

    hashed_pw = bcrypt.hashpw(request.password.encode("utf8"), bcrypt.gensalt())
    decoded_hash_pw = hashed_pw.decode("utf8")

    user_id = await UserService().create_user(
        request.name,
        request.nickname,
        temp_sms_auth.phone,
        request.email,
        decoded_hash_pw
    )

    token_helper = TokenHelper()
    access_token = token_helper.encode({"user_id": user_id}, expire_period=config.JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
    refresh_token = token_helper.encode({"user_id": user_id}, expire_period=config.JWT_REFRESH_TOKEN_EXPIRE_SECONDS)

    background_tasks.add_task(cleanup_temp_sms_auth, request.session_id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@user_router.get(
    "/profile",
    response_model=UserProfileResponseSchema,
    response_model_exclude={"id"},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
async def get_user_profile(request: Request):
    user = await UserService().get_user(request.user.id)
    return user.__dict__


@user_router.post(
    "/login"
)
async def login_user(request: UserLoginRequestSchema):
    if request.phone:
        user = await UserService().get_user_by_phone(request.phone)
    else:
        user = await UserService().get_user_by_email(request.email)

    if not user:
        raise UnauthorizedException("user not matched")

    pw_matched = bcrypt.checkpw(request.password.encode("utf8"), user.password.encode("utf8"))
    if pw_matched:
        token_helper = TokenHelper()
        access_token = token_helper.encode({"user_id": user.id}, expire_period=config.JWT_ACCESS_TOKEN_EXPIRE_SECONDS)
        refresh_token = token_helper.encode({"user_id": user.id}, expire_period=config.JWT_REFRESH_TOKEN_EXPIRE_SECONDS)
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise UnauthorizedException("password not matched")


@user_router.put(
    "/password"
)
async def reset_password(request: PasswordResetRequestSchema, background_tasks: BackgroundTasks):
    temp_sms_auth = await UserService().get_temp_sms_auth(request.session_id)
    if not temp_sms_auth:
        raise NotFoundException(message="session_id not found")

    if not temp_sms_auth.is_verified:
        raise UnauthorizedException(message="phone number not verified")

    user = await UserService().get_user_by_phone(temp_sms_auth.phone)
    if not user:
        raise NotFoundException("user not found")

    new_hashed_pw = bcrypt.hashpw(request.password.encode("utf8"), bcrypt.gensalt())
    new_decoded_pw = new_hashed_pw.decode("utf8")
    await UserService().reset_password(user.id, new_decoded_pw)

    background_tasks.add_task(cleanup_temp_sms_auth, request.session_id)
    return {"is_password_reset": True}
