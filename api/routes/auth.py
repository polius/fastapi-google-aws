import os
import uuid
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from ..utils import create_token, decode_token

router = APIRouter(tags=["Auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@router.get(
    "/login",
    summary="Start Google OAuth2 login",
    description=(
        "Initiates the Google OAuth2 authentication process.\n\n"
        "Redirects the user to Google's login/consent page.\n\n"
        "After successful authentication, the user is redirected to `/callback`."
    )
)
async def login(request: Request):
    if request.cookies.get("token"):
        return RedirectResponse(url="/welcome")

    redirect_uri = request.url_for('callback')
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile"
    return RedirectResponse(url=google_auth_url)

@router.get(
    "/callback",
    summary="Handle Google OAuth2 callback",
    description=(
        "Handles the callback from Google OAuth2 after successful login.\n\n"
        "This endpoint exchanges the authorization code for a token, retrieves the user profile, and sets the authentication cookie or session.\n\n"
        "Users are typically redirected to the main application after this step."
    )
)
async def callback(code: str, request: Request):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": str(request.url_for("callback")),
                "grant_type": "authorization_code",
            },
        )

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code for token")

    # Get token information
    resp_data = resp.json()
    id_token_value = resp_data.get("id_token")
    access_token_value = resp_data.get("access_token")

    # Verify Google ID token
    id_info = id_token.verify_oauth2_token(id_token_value, google_requests.Request(), GOOGLE_CLIENT_ID)

    # [Optional: Restrict access to specified emails or domains]
    # if id_info.get("email") != '...':
    #     raise HTTPException(403, "Your account is not allowed to access this app")

    # Generate a session_id
    session_id = str(uuid.uuid4())

    # Store the session in the backend
    request.app.state.sessions[session_id] = {
        "access_token": access_token_value,
        "id_token": id_token_value,
        "id_info": id_info,
    }

    # Create your own signed JWT access token
    token = create_token({
        "session": session_id,
        "email": id_info.get("email"),
        "name": id_info.get("name"),
    })

    # Define redirect URL
    response = RedirectResponse(url='/welcome')

    # Set JWT as an HTTP-only cookie
    response.set_cookie(key="token", value=token, expires=datetime.now(timezone.utc) + timedelta(minutes=60), httponly=True, samesite='strict')

    # Return the response with access token and refresh token in the cookie
    return response

@router.get(
    "/logout",
    summary="Log out the current user",
    description=(
        "Logs out the authenticated user by clearing the session or authentication cookie.\n\n"
        "After logging out, the user will no longer be able to access protected endpoints."
    )
)
async def logout(request: Request):
    token = request.cookies.get("token")
    if token:
        decoded_token = decode_token(token)

        if decoded_token['session'] in request.app.state.sessions:
            access_token = request.app.state.sessions[decoded_token['session']]

            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": access_token},
                    headers={"content-type": "application/x-www-form-urlencoded"}
                )

    # Delete cookie & redirect
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="token")
    return response
