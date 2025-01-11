from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoticeResponse(BaseModel):
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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
