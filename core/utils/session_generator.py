import uuid


def generate_random_session_id() -> str:
    random_ids = str(uuid.uuid4()).split('-')
    session_id = random_ids[0] + random_ids[-1]
    return session_id
