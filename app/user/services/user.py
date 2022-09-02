import datetime as dt

from typing import Union
from sqlalchemy import select, update, delete

from app.user.models import User, TempSMSAuth
from core.db import Transactional, session


class UserService:
    @Transactional()
    async def create_user(
            self,
            name: str,
            nickname: str,
            phone: str,
            email: str,
            password: str
    ) -> User:
        user = User(
            name=name,
            nickname=nickname,
            phone=phone,
            email=email,
            password=password
        )
        session.add(user)
        await session.flush()
        return user

    async def get_user(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()
        return user

    async def get_user_by_phone(self, phone: str) -> Union[User, None]:
        query = select(User).where(User.phone == phone)
        result = await session.execute(query)
        user = result.scalars().first()
        return user

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalars().first()
        return user

    @Transactional()
    async def create_temp_sms_auth(
            self,
            session_id: str,
            phone: str,
            auth_code: str,
            code_sent_at: dt.datetime
    ) -> None:
        temp_sms_auth = TempSMSAuth(
            session_id=session_id,
            phone=phone,
            auth_code=auth_code,
            code_sent_at=code_sent_at
        )
        session.add(temp_sms_auth)

    async def get_temp_sms_auth(self, session_id: str) -> Union[TempSMSAuth, None]:
        query = select(TempSMSAuth).where(TempSMSAuth.session_id == session_id)
        result = await session.execute(query)
        temp_sms_auth = result.scalars().first()
        return temp_sms_auth

    @Transactional()
    async def set_verified_flag(self, session_id: str) -> None:
        query = (
            update(TempSMSAuth).
            where(TempSMSAuth.session_id == session_id).
            values(is_verified=True)
        )
        await session.execute(query)

    @Transactional()
    async def delete_temp_sms_auth(self, session_id: str) -> None:
        query = delete(TempSMSAuth).where(TempSMSAuth.session_id == session_id)
        await session.execute(query)
