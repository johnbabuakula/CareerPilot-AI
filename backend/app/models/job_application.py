
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    company_name = Column(String(150), nullable=False)
    job_role = Column(String(150), nullable=False)

    status = Column(
        String(50),
        default="Applied",
        nullable=False
    )

    application_date = Column(Date, nullable=False)

    job_description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User", backref="job_applications")
