import uuid
from typing import Optional
from datetime import datetime, timedelta
from itsdangerous import URLSafeSerializer
from app.core.config import settings

serializer = URLSafeSerializer(settings.SECRET_KEY)

def generate_uuid() -> str:
    return str(uuid.uuid4())

def create_session_token(user_id: str, timestamp: Optional[float] = None) -> str:
    if timestamp is None:
        timestamp = datetime.utcnow().timestamp()
    
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    
    return f"{user_id}.{timestamp}.{signature}"

def verify_session_token(token: str) -> tuple[bool, Optional[str], Optional[float]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False, None, None
        
        user_id, timestamp_str, signature = parts
        timestamp = float(timestamp_str)
        
        expected_data = f"{user_id}.{timestamp}"
        verified_data = serializer.loads(signature)
        
        if verified_data != expected_data:
            return False, None, None
        
        return True, user_id, timestamp
    except Exception:
        return False, None, None

def check_session_validity(last_activity: float) -> tuple[bool, str]:
    now = datetime.utcnow().timestamp()
    time_diff = now - last_activity
    
    if time_diff > 300:  # Больше 5 минут
        return False, 'expired'
    elif time_diff >= 180:  # Между 3 и 5 минутами
        return True, 'renew'
    else:  # Меньше 3 минут
        return True, 'valid'

def generate_server_time() -> str:
    return datetime.utcnow().isoformat()