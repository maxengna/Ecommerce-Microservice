from fastapi import HTTPException, status
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import time

# JWT Configuration (same as user service)
SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
ALGORITHM = "HS256"

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def extract_token_from_header(authorization: str) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]

def is_token_expired(payload: Dict[str, Any]) -> bool:
    """Check if token is expired."""
    exp = payload.get("exp")
    if not exp:
        return False  # No expiration claim
    
    return time.time() > exp

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Get user information from token."""
    payload = verify_token(token)
    if not payload:
        return None
    
    if is_token_expired(payload):
        return None
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }
