from sqlalchemy import Column, Boolean, String, Integer, DateTime

from core.db import Base
from core.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)


class TempSMSAuth(Base):
    __tablename__ = "temp_sms_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    phone = Column(String(255), nullable=False)
    auth_code = Column(String(255), nullable=False)
    code_sent_at = Column(DateTime, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
