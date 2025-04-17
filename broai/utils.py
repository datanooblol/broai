from datetime import datetime
from zoneinfo import ZoneInfo  # Available in Python 3.9+

def get_timestamp():
    dt = datetime.now(ZoneInfo("Asia/Bangkok"))
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')