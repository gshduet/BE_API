from typing import Optional

from sqlmodel import Field, SQLModel, Column, Text

from models.commons import TimeStamp


class Quest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quest_number: int = Field(default=0)
    title: str = Field(default="")
    content: str = Field(default="", sa_column=Column(Text, nullable=True))
    input_example: str = Field(default="", sa_column=Column(Text, nullable=True))
    output_example: str = Field(default="", sa_column=Column(Text, nullable=True))


class QuestResult(TimeStamp, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quest_number: int = Field(default=0)
    user_name: str = Field(default="")
    user_email: str = Field(default="")
    time_taken: str = Field(default="00:00:00")
