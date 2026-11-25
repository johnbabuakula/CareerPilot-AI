
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class JobApplicationCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    job_role: str = Field(min_length=2, max_length=150)
    status: str = "Applied"
    application_date: date
    job_description: str | None = None


class JobApplicationResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    job_role: str
    status: str
    application_date: date
    job_description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
