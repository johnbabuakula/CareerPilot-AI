
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ReminderCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str | None = None
    reminder_type: str = Field(min_length=2, max_length=50)
    reminder_date: datetime


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    reminder_type: str | None = Field(default=None, min_length=2, max_length=50)
    reminder_date: datetime | None = None
    is_completed: bool | None = None


class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    reminder_type: str
    reminder_date: datetime
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
