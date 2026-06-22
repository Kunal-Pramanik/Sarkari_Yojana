from supabase import create_client, Client
from fastapi import HTTPException, Header
from pydantic import BaseModel
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# --- Request models ---
class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str

class SignInRequest(BaseModel):
    email: str
    password: str

# --- Sign up ---
def sign_up(data: SignUpRequest):
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {"full_name": data.full_name}
            }
        })
        if res.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "message": "Account created successfully",
            "user_id": res.user.id,
            "email": res.user.email
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Sign in ---
def sign_in(data: SignInRequest):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        if res.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "access_token": res.session.access_token,
            "user_id": res.user.id,
            "email": res.user.email,
            "full_name": res.user.user_metadata.get("full_name", "")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

# --- Verify token (used to protect routes) ---
def get_current_user(authorization: str = Header(...)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        
        if user is None or user.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "user_id": user.user.id,
            "email": user.user.email,
            "full_name": user.user.user_metadata.get("full_name", "")
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate token")