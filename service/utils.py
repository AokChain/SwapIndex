from datetime import datetime
from uuid import uuid4

def get_uuid():
    return str(uuid4())

def log_message(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}")