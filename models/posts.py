from typing import Optional
from datetime import datetime

from sqlmodel import Field
from pydantic import BaseModel

from models.commons import TimeStamp, SoftDelete


class Notice(TimeStamp, SoftDelete, table=True):
    """
    공지사항 모델입니다.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="")
    content: str = Field(default="")
    author_name: str = Field(default="")
    author_google_id: str = Field(index=True)  # User 모델의 google_id와 매칭되는 필드


class GuestBook(TimeStamp, SoftDelete, table=True):
    """
    방명록 모델입니다.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(default="")
    author_name: str = Field(default="")
    guest_google_id: str = Field(index=True)  # 방명록을 작성한 사용자의 google_id
    host_google_id: str = Field(index=True)  # 방명록이 작성된 대상 사용자의 google_id
    is_secret: bool = Field(default=False, description="비밀 방명록 여부")
