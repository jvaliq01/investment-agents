from datetime import datetime, timezone
import uuid


def generate_id(prefix: str | None = None) -> str:
    """
    UTC-timestamped, collision-safe ID, e.g.:
    >>> generate_id("resp")
    'resp_20250629T213217Z_94d2ef61'
    """
    core = uuid.uuid4().hex 
    return f"{prefix}_{core}" if prefix else core

def gen_cur_timestamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')



     

