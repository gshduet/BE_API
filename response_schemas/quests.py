from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuestResponse(BaseModel):
    quest_number: int
    title: str
    content: str
    input_example: str
    output_example: str


class QuestResultResponse(BaseModel):
    quest_number: int
    user_name: str
    user_email: str
    time_taken: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
