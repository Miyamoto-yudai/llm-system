import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from src.database.connection import get_database
from src.database.models import UserModel, SessionModel
from bson import ObjectId

load_dotenv()

# Password hashing with Argon2 (modern best practice)
ph = PasswordHasher()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here_change_in_production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password using Argon2"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2"""
    return ph.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    """Decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def authenticate_user(email: str, password: str):
    """Authenticate a user by email and password"""
    db = get_database()

    if db is None:
        return False

    user = await db.users.find_one({"email": email})

    if not user:
        return False

    if not verify_password(password, user["password_hash"]):
        return False

    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Verify session is still valid
    db = get_database()
    if db is None:
        raise credentials_exception

    session = await db.sessions.find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not session:
        raise credentials_exception

    # Get user from database
    session_user_id = session.get("user_id")

    query = {"_id": session_user_id}
    if isinstance(session_user_id, str) and ObjectId.is_valid(session_user_id):
        query = {"_id": ObjectId(session_user_id)}

    user = await db.users.find_one(query)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get the current user if authenticated, otherwise return None"""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def create_session(user_id: str, request_info: dict = None) -> str:
    """Create a new session for a user"""
    db = get_database()

    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    expires_at = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    token = create_access_token({"sub": str(user_id)})

    session = SessionModel(
        user_id=str(user_id),
        token=token,
        expires_at=expires_at,
        ip_address=request_info.get("ip_address") if request_info else None,
        user_agent=request_info.get("user_agent") if request_info else None
    )

    await db.sessions.insert_one(session.model_dump(by_alias=True))

    return token


async def invalidate_session(token: str):
    """Invalidate a session by token"""
    db = get_database()
    await db.sessions.delete_one({"token": token})


async def clean_expired_sessions():
    """Remove expired sessions from database"""
    db = get_database()
    result = await db.sessions.delete_many({
        "expires_at": {"$lt": datetime.utcnow()}
    })
    return result.deleted_count
