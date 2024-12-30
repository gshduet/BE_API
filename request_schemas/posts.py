from pydantic import BaseModel


class NoticeCreate(BaseModel):
    title: str
    content: str


class GuestBookCreate(BaseModel):
    host_google_id: str
    content: str
    is_secret: bool = False
