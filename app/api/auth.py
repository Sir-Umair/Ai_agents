from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
import requests
import urllib.parse
from datetime import datetime
from app.config import settings
from app.db import users_collection
from app.services.security_service import encrypt_data
from jose import jwt

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

@router.get("/login")
async def login():
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")
        
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(code: str, state: str = None):
    try:
        # 1. Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        token_resp = requests.post(token_url, data=payload)
        if not token_resp.ok:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")
        
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        # 2. Get user info
        user_info_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_resp.json()
        email = user_info.get("email")
        name = user_info.get("name")
        
        # 3. Encrypt and Prepare Update
        update_doc = {
            "email": email,
            "name": name,
            "access_token": encrypt_data(access_token),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "scopes": SCOPES,
            "last_login": datetime.utcnow()
        }
        
        # Only overwrite refresh_token if we actually got a new one
        if refresh_token:
            update_doc["refresh_token"] = encrypt_data(refresh_token)
        
        if users_collection is None:
            raise HTTPException(status_code=500, detail="Database connection not established")
            
        await users_collection.update_one(
            {"email": email},
            {"$set": update_doc},
            upsert=True
        )
        
        # 4. Generate JWT
        token = jwt.encode({"sub": email}, settings.secret_key, algorithm="HS256")
        
        # 5. Redirect to Frontend
        return RedirectResponse(url=f"{settings.frontend_url}/auth/callback?token={token}&email={email}")
    except Exception as e:
        error_msg = str(e)
        print(f"Error in OAuth callback: {type(e).__name__}: {error_msg}")
        
        # provide a more user-friendly error for common DNS/connection issues
        if "DNS" in error_msg or "resolution lifetime expired" in error_msg:
             error_msg = "Database connection timed out during DNS resolution. This is often caused by local network restrictions or slow DNS servers. We've attempted to use a custom resolver, please try again."
        
        if isinstance(e, HTTPException): 
            raise e
        raise HTTPException(status_code=500, detail=f"Authentication failed: {error_msg}")

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        print("[Auth] Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email = payload.get("sub")
        
        if not users_collection:
            print("[Auth] ERROR: users_collection is None. Check MongoDB connection.")
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        user = await users_collection.find_one({"email": email})
        if not user:
            print(f"[Auth] User not found in DB: {email}")
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.JWTError as e:
        print(f"[Auth] JWT Decode Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"[Auth] Unexpected error in get_current_user: {type(e).__name__}: {e}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status")
async def get_status(user: dict = Depends(get_current_user)):
    """Compatibility endpoint for status check."""
    return {"authenticated": True, "email": user.get("email")}

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Returns the current user profile, excluding all sensitive tokens and secrets."""
    user["_id"] = str(user["_id"])
    
    # Strictly define what we return to the frontend
    safe_user = {
        "id": user["_id"],
        "email": user["email"],
        "name": user.get("name", ""),
        "last_login": user.get("last_login"),
        "scopes": user.get("scopes", []),
        # Do NOT return access_token, refresh_token, client_id, or client_secret
    }
    return safe_user
