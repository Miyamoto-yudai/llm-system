import os
import re
import secrets
import httpx
from typing import Optional, Dict
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from src.database.connection import get_database, connect_to_mongo
from src.database.models import UserModel
from src.auth.authentication import create_session
from datetime import datetime

load_dotenv()

# OAuth configuration
oauth = OAuth()

# Configure Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


async def get_google_user_info(access_token: str) -> Optional[Dict]:
    """Get user information from Google using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code == 200:
            return response.json()
        return None


async def get_or_create_oauth_user(provider: str, provider_user_id: str, email: str, name: str, picture: Optional[str] = None):
    """Get existing user or create new one from OAuth provider data"""
    db = get_database()

    if db is None:
        # Fallback for cases where the Mongo connection hasn't been initialised yet
        await connect_to_mongo()
        db = get_database()

    if db is None:
        raise RuntimeError("MongoDB connection is not initialized")

    # First check if user exists with this provider ID
    user = await db.users.find_one({
        "oauth_providers.provider": provider,
        "oauth_providers.provider_user_id": provider_user_id
    })

    if user:
        # Update last login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return user

    # Check if user exists with same email
    user = await db.users.find_one({"email": email})

    if user:
        # Link OAuth provider to existing account
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$push": {
                    "oauth_providers": {
                        "provider": provider,
                        "provider_user_id": provider_user_id
                    }
                },
                "$set": {
                    "last_login": datetime.utcnow()
                }
            }
        )
        return await db.users.find_one({"_id": user["_id"]})

    # Create new user
    def _generate_username(display_name: str, email_address: str) -> str:
        # Prefer display name, keep unicode, replace whitespace with underscore
        base = re.sub(r"\s+", "_", display_name.strip())
        if len(base) < 3:
            # Fall back to email local-part
            local_part = email_address.split("@")[0]
            base = re.sub(r"\s+", "_", local_part)
        if len(base) < 3:
            base = f"user_{secrets.token_hex(3)}"
        # Trim to reasonable length
        return base[:50]

    generated_username = _generate_username(name or "user", email)

    user_model = UserModel(
        username=generated_username,
        email=email,
        password_hash="OAUTH_USER",  # OAuth users don't have passwords
        oauth_providers=[{
            "provider": provider,
            "provider_user_id": provider_user_id
        }],
        profile_picture=picture
    )

    # Check if username already exists and make it unique
    base_username = user_model.username
    counter = 1
    while await db.users.find_one({"username": user_model.username}):
        user_model.username = f"{base_username}_{counter}"
        counter += 1

    result = await db.users.insert_one(user_model.model_dump(by_alias=True))
    return await db.users.find_one({"_id": result.inserted_id})


async def handle_google_callback(code: str, request_info: dict = None) -> dict:
    """Handle Google OAuth callback"""
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
                'grant_type': 'authorization_code'
            }
        )

        if token_response.status_code != 200:
            raise Exception("Failed to exchange code for token")

        tokens = token_response.json()
        access_token = tokens.get('access_token')

        # Get user info
        user_info = await get_google_user_info(access_token)

        if not user_info:
            raise Exception("Failed to get user information from Google")

        # Get or create user
        user = await get_or_create_oauth_user(
            provider='google',
            provider_user_id=user_info.get('id'),
            email=user_info.get('email'),
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )

        # Create session
        session_token = await create_session(str(user["_id"]), request_info)

        return {
            "access_token": session_token,
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "profile_picture": user.get("profile_picture")
            }
        }


def get_google_auth_url() -> str:
    """Get Google OAuth authorization URL"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={os.getenv('GOOGLE_CLIENT_ID')}&"
        f"redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return google_auth_url
