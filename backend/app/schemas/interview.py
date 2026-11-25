
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InterviewSessionCreate(BaseModel):
    job_role: str = Field(min_length=2, max_length=150)
    topic: str = Field(min_length=2, max_length=100)
    total_questions: int = Field(default=5, ge=1, le=10)


class InterviewQuestionResponse(BaseModel):
    id: int
    question: str
    user_answer: str | None
    feedback: str | None
    score: int

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionResponse(BaseModel):
    id: int
    job_role: str
    topic: str
    total_questions: int
    score: int
    created_at: datetime
    questions: list[InterviewQuestionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class AnswerSubmit(BaseModel):
    answer: str = Field(min_length=1)
