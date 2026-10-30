from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings

def get_password_hash(password: str) -> str:
    """
    Takes a plain text password, generates a unique salt,
    and returns the one-way bcrypt hash string.
    """
    # bcrypt requires bytes, so we encode the string to UTF-8
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if the entered plain-text password matches the stored bcrypt hash.
    Returns True if valid, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    # bcrypt only processes the first 72 bytes; reject longer passwords instead
    # of allowing silent truncation or a backend exception.
    if len(password_bytes) > 72:
        return False
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    """
    Generates a cryptographically signed JWT token (the "digital wristband").
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(subject),  # "sub" stands for Subject (the user's ID)
        "exp": expire         # "exp" stands for Expiration time
    }
    
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
