
from app.database.connection import Base, engine

# Import models so SQLAlchemy can create their tables
from app.models.user import User
from app.models.job_application import JobApplication
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.reminder import Reminder


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
