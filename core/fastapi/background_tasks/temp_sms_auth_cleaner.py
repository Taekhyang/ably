from core.db.standalone_session import standalone_session
from app.user.services import UserService


@standalone_session
async def cleanup_temp_sms_auth(session_id):
    await UserService().delete_temp_sms_auth(session_id)
