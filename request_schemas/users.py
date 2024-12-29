from pydantic import BaseModel, EmailStr
from typing import Optional, List


class GoogleSignupRequest(BaseModel):
    email: EmailStr
    name: str
    google_id: str


class UserProfileUpdateRequest(BaseModel):
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
