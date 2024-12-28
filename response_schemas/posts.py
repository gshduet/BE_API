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

    # ConfigDict를 사용하여 설정을 정의합니다.
    model_config = ConfigDict(from_attributes=True)
