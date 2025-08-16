from dotenv import load_dotenv
load_dotenv()
import os

# This file will encapsulate the OAuth flow and profile fetching.

from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

router = APIRouter()

# Initialize OAuth client for LinkedIn
oauth = OAuth()
oauth.register(
    name='linkedin',
    client_id=os.environ.get("LINKEDIN_CLIENT_ID"),
    client_secret=os.environ.get("LINKEDIN_CLIENT_SECRET"),
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={
        'scope': 'w_member_social'
    }
)

@router.get("/login")
async def linkedin_login(request: Request):
# Redirect the user to LinkedIn's OAuth login page.

    redirect_uri = "http://localhost:8000/linkedin/auth"

    print(redirect_uri)
    return await oauth.linkedin.authorize_redirect(request, redirect_uri)

@router.get("/auth", name="linkedin_auth")
async def linkedin_auth(request: Request):
# OAuth callback from LinkedIn — this exchanges the code for an access token.
    try:
        token = await oauth.linkedin.authorize_access_token(
            request,
            client_secret=os.environ.get("LINKEDIN_CLIENT_SECRET")
        )

    except Exception as e:
        print("OAuth error:", e)
        raise HTTPException(status_code=400, detail="OAuth authorization failed")

    # Store the token in the session for later API calls
    # Note: Requires session middleware in your FastAPI app
    request.session['token'] = token
    return RedirectResponse(url="/linkedin/profile")

@router.get("/profile")
async def get_profile(request: Request):
# Get the LinkedIn profile data of the authenticated user using stored token.

    token = request.session.get('token')
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated with LinkedIn")

    # Fetch the LinkedIn basic profile
    try:
        resp = await oauth.linkedin.get('me', token= token)
    except Exception:
        raise HTTPException(status_code=500, detail= "Failed to fetch profile data")

    profile_data = resp.json()
    # Optionally fetch email
    email_resp = await oauth.linkedin.get(
        "emailAddress?q=members&projection=(elements*(handle~))", token=token
    )
    email_data = email_resp.json()
    profile_data['email'] = email_data.get('elements', [{}])[0].get('handle~', {}).get('emailAddress')

    return profile_data
