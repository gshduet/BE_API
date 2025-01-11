from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Column, ARRAY, String

from models.commons import TimeStamp


class User(TimeStamp, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str = Field(default="")
    google_id: str = Field(unique=True, index=True)
    google_image_url: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    generation: int = Field(default=0, nullable=True)
    last_login_at: Optional[datetime] = None
    role_level: int = Field(default=0)


class UserProfile(TimeStamp, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(index=True)
    bio: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    resume_url: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    portfolio_url: List[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(String))
    )
    tech_stack: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
