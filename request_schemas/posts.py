from pydantic import BaseModel


class NoticeCreate(BaseModel):
    title: str
    content: str


class GuestBookCreate(BaseModel):
    content: str
    is_secret: bool = False
