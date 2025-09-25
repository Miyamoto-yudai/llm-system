import os
import logging
from typing import Optional
from datetime import datetime
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from src.auth.oauth import get_google_auth_url, handle_google_callback
from src.database.models import TokenResponse, UserResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["oauth"])


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    request: Request = None
):
    """Handle Google OAuth callback"""
    try:
        # Get request info for session creation
        request_info = {
            "ip_address": request.client.host if request else None,
            "user_agent": request.headers.get("user-agent") if request else None
        }

        # Handle the callback and get user data
        auth_data = await handle_google_callback(code, request_info)

        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        redirect_url = f"{frontend_url}/auth/callback?token={auth_data['access_token']}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logging.exception("Google OAuth callback error")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        safe_message = quote(str(e) or "Authentication failed")
        error_url = f"{frontend_url}/auth/error?message={safe_message}"
        return RedirectResponse(url=error_url)


@router.post("/google/token")
async def google_token_login(code: str, request: Request):
    """Exchange Google authorization code for token (for popup/redirect flow)"""
    try:
        # Get request info for session creation
        request_info = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }

        # Handle the callback and get user data
        auth_data = await handle_google_callback(code, request_info)

        # Return token response
        user_response = UserResponse(
            id=auth_data["user"]["id"],
            username=auth_data["user"]["username"],
            email=auth_data["user"]["email"],
            created_at=datetime.utcnow(),
            is_active=True
        )

        return TokenResponse(
            access_token=auth_data["access_token"],
            user=user_response
        )

    except Exception as e:
        print(f"Google token exchange error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with Google"
        )
