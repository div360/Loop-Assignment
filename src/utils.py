import pytz
from datetime import datetime

def convert_to_local_time(time: datetime, timezone_str: str) -> datetime:
    
    target_tz = pytz.timezone(timezone_str)
    # Convert the datetime to the target timezone
    local_dt = time.astimezone(target_tz)
    return local_dt

def convert_to_utc(time: datetime, timezone_str: str) -> datetime:
    # Get the target time zone
    target_tz = pytz.timezone(timezone_str)
    
    # Convert the datetime to UTC
    utc_time = time.astimezone(pytz.utc)
    
    return utc_time