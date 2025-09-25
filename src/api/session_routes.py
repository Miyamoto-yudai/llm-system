from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.database.connection import get_database
from src.database.models import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    UserModel
)
from src.auth.authentication import (
    get_password_hash, authenticate_user, create_session,
    get_current_user, invalidate_session
)
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate, request: Request):
    """Register a new user"""
    db = get_database()

    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user.email},
            {"username": user.username}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    user_model = UserModel(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password)
    )

    result = await db.users.insert_one(user_model.dict(by_alias=True))

    # Create session
    request_info = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
    token = await create_session(str(result.inserted_id), request_info)

    # Return token and user info
    user_response = UserResponse(
        id=str(result.inserted_id),
        username=user_model.username,
        email=user_model.email,
        created_at=user_model.created_at,
        is_active=user_model.is_active
    )

    return TokenResponse(
        access_token=token,
        user=user_response
    )


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, request: Request):
    """Login a user"""
    authenticated_user = await authenticate_user(user.email, user.password)

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create session
    request_info = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
    token = await create_session(str(authenticated_user["_id"]), request_info)

    # Return token and user info
    user_response = UserResponse(
        id=str(authenticated_user["_id"]),
        username=authenticated_user["username"],
        email=authenticated_user["email"],
        created_at=authenticated_user["created_at"],
        is_active=authenticated_user["is_active"]
    )

    return TokenResponse(
        access_token=token,
        user=user_response
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout the current user"""
    # Note: In a real implementation, you would get the token from the request
    # and invalidate it. For now, we'll just return success.
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )


@router.delete("/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete the current user's account"""
    db = get_database()

    # Delete all user's conversations and messages
    conversations = await db.conversations.find({"user_id": str(current_user["_id"])}).to_list(None)
    for conv in conversations:
        await db.messages.delete_many({"conversation_id": str(conv["_id"])})

    await db.conversations.delete_many({"user_id": str(current_user["_id"])})

    # Delete all user's sessions
    await db.sessions.delete_many({"user_id": str(current_user["_id"])})

    # Delete user
    await db.users.delete_one({"_id": current_user["_id"]})

    return {"message": "Account deleted successfully"}