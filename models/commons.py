from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class TimeStamp(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )


class SoftDelete(SQLModel):
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()
