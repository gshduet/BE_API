from pydantic import BaseModel
from typing import Optional, List


class GoogleSignupRequest(BaseModel):
    email: str
    name: str
    google_id: str
    google_image_url: Optional[str]


class UserProfileUpdateRequest(BaseModel):
    bio: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
