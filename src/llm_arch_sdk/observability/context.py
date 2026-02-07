import secrets
import string
import uuid

def new_session_id() -> str:
    return f"session-{uuid.uuid4()}"

def new_job_id() -> str:
    return f"job-{uuid.uuid4()}"

def new_trace_id() -> str:
    return f"trace-{uuid.uuid4()}"

def _new_short_name(length: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def new_user_id() -> str:
    return f"user-{_new_short_name()}"

def new_agent_id() -> str:
    return f"agent-{_new_short_name()}"