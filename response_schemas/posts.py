from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoticeResponse(BaseModel):
    """
    게시글 응답에 사용되는 스키마입니다.
    """

    id: int
    title: str
    content: str
    author_name: str
    author_google_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GuestBookResponse(BaseModel):
    id: int
    content: str
    author_name: str
    # is_secret: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
