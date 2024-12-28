from datetime import datetime
from typing import Optional

from sqlmodel import Field

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
    is_active: bool = Field(default=True)  # 계정 활성화 상태
