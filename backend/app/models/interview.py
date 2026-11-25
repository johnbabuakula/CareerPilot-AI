
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    job_role = Column(String(150), nullable=False)
    topic = Column(String(100), nullable=False)

    total_questions = Column(Integer, default=5)
    score = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        nullable=False
    )

    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    score = Column(Integer, default=0)

    session = relationship(
        "InterviewSession",
        back_populates="questions"
    )
