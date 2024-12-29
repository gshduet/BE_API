from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Column, ARRAY, String

from models.commons import TimeStamp


class User(TimeStamp, table=True):
    """
    Google OAuth를 통해 가입하는 사용자 정보를 저장하는 모델입니다.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str = Field(default="")
    google_id: str = Field(unique=True, index=True)
    generation: int = Field(default=0, nullable=True)
    last_login_at: Optional[datetime] = None
    role_level: int = Field(default=0)


class UserProfile(TimeStamp, table=True):
    """
    사용자의 부가 정보를 저장하는 모델입니다.
    google_id를 통해 User 테이블과 연관 관계를 가집니다.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(index=True)
    bio: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    portfolio_url: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    resume_url: Optional[str] = Field(
        default=None, sa_column=Column(String, nullable=True)
    )
    tech_stack: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(String), nullable=True)
    )
