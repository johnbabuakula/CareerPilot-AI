
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user

from app.models.interview import InterviewSession, InterviewQuestion

from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    AnswerSubmit
)

from app.utils.interview_generator import generate_questions
from app.utils.answer_evaluator import evaluate_answer


router = APIRouter(
    prefix="/interviews",
    tags=["Interview Preparation"]
)


# Create a new interview session
@router.post("/", response_model=InterviewSessionResponse)
def create_interview(
    data: InterviewSessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    questions = generate_questions(
        data.topic,
        data.total_questions
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported interview topic."
        )

    session = InterviewSession(
        user_id=current_user.id,
        job_role=data.job_role,
        topic=data.topic,
        total_questions=len(questions)
    )

    db.add(session)
    db.flush()

    for question in questions:
        new_question = InterviewQuestion(
            session_id=session.id,
            question=question
        )

        db.add(new_question)

    db.commit()
    db.refresh(session)

    return session


# Get all interview sessions of the logged-in user
@router.get("/", response_model=list[InterviewSessionResponse])
def get_interviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(
        InterviewSession.created_at.desc()
    ).all()

    return sessions


# Submit and evaluate an interview answer
@router.post("/{session_id}/questions/{question_id}/answer")
def submit_answer(
    session_id: int,
    question_id: int,
    data: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Find the session belonging to the logged-in user
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    # Find the question inside that session
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.session_id == session_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found."
        )

    # Prevent duplicate answer submissions
    if question.user_answer is not None:
        raise HTTPException(
            status_code=409,
            detail="You have already submitted an answer for this question."
        )

    # Evaluate the submitted answer
    evaluation = evaluate_answer(
        data.answer,
        question.question
    )

    # Save answer and evaluation
    question.user_answer = data.answer
    question.feedback = evaluation["feedback"]
    question.score = evaluation["score"]

    # Calculate average score of answered questions
    db.flush()

    answered_questions = [
        q for q in session.questions
        if q.user_answer is not None
    ]

    if answered_questions:
        session.score = round(
            sum(q.score for q in answered_questions)
            / len(answered_questions)
        )

    db.commit()
    db.refresh(question)
    db.refresh(session)

    return {
        "message": "Answer evaluated successfully!",
        "question_id": question.id,
        "score": question.score,
        "feedback": question.feedback,
        "session_score": session.score
    }


# Get the completion summary of an interview
@router.get("/{session_id}/summary")
def get_interview_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Find the interview session belonging to the logged-in user
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found."
        )

    # Separate answered and unanswered questions
    answered_questions = [
        question for question in session.questions
        if question.user_answer is not None
    ]

    total_questions = len(session.questions)
    answered_count = len(answered_questions)
    pending_count = total_questions - answered_count

    # Calculate average score
    if answered_questions:
        average_score = round(
            sum(question.score for question in answered_questions)
            / answered_count,
            2
        )
    else:
        average_score = 0

    # Convert the score out of 10 into a percentage
    percentage = round(average_score * 10, 2)

    # Determine performance level
    if answered_count == 0:
        performance = "Not Started"
    elif percentage >= 80:
        performance = "Excellent"
    elif percentage >= 60:
        performance = "Good"
    elif percentage >= 40:
        performance = "Average"
    else:
        performance = "Needs Improvement"

    return {
        "session_id": session.id,
        "job_role": session.job_role,
        "topic": session.topic,
        "total_questions": total_questions,
        "answered_questions": answered_count,
        "pending_questions": pending_count,
        "average_score": average_score,
        "percentage": percentage,
        "performance": performance,
        "completed": pending_count == 0
    }
