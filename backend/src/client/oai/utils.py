from datetime import datetime, timezone




def generate_id(prefix: str | None = None) -> None:
    """
    UTC-timestamped, collision-safe ID, e.g.:
    >>> generate_id("resp")
    'resp_20250629T213217Z_94d2ef61'
    """
    core = uuid.uuid4().hex 
    return f"{prefix}_{core}" if prefix else core

def gen_cur_timestamp() -> None:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')