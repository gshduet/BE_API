from pydantic import BaseModel
from typing import Optional, List


class UserProfileResponse(BaseModel):
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
