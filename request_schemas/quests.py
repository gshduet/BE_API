from pydantic import BaseModel


class QuestResultCreateRequest(BaseModel):
    time_taken: str
