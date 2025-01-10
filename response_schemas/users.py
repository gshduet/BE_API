from pydantic import BaseModel
from typing import Optional, List


class UserProfileResponse(BaseModel):
    bio: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None


class UserListResponse(BaseModel):
    name: str
    google_id: str
    generation: int
