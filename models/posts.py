from typing import Optional

from sqlmodel import Field

from models.commons import TimeStamp, SoftDelete


class Notice(TimeStamp, SoftDelete, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="")
    content: str = Field(default="")
    author_name: str = Field(default="")
    author_google_id: str = Field(index=True)


class GuestBook(TimeStamp, SoftDelete, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(default="")
    author_name: str = Field(default="")
    guest_google_id: str = Field(index=True)
    host_google_id: str = Field(index=True)
    is_secret: bool = Field(default=False, description="비밀 방명록 여부")
