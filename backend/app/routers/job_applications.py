
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job_application import JobApplication
from app.schemas.job_application import (
    JobApplicationCreate,
    JobApplicationResponse
)

router = APIRouter(
    prefix="/applications",
    tags=["Job Applications"]
)


# ADD A JOB APPLICATION
@router.post(
    "/",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_application(
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_application = JobApplication(
        user_id=current_user.id,
        company_name=application_data.company_name,
        job_role=application_data.job_role,
        status=application_data.status,
        application_date=application_data.application_date,
        job_description=application_data.job_description
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


# GET ALL APPLICATIONS OF LOGGED-IN USER
@router.get(
    "/",
    response_model=list[JobApplicationResponse]
)
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()

    return applications


# CAREER ANALYTICS
@router.get("/analytics")
def get_application_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()

    total_applications = len(applications)

    status_counts = {
        "Applied": 0,
        "Assessment": 0,
        "Interview": 0,
        "Selected": 0,
        "Rejected": 0
    }

    monthly_counts = defaultdict(int)
    company_counts = defaultdict(lambda: {
        "applications": 0,
        "interviews": 0,
        "offers": 0,
        "rejections": 0
    })

    for application in applications:
        application_status = application.status.strip().title()
        company_name = application.company_name.strip()

        # Status breakdown
        if application_status in status_counts:
            status_counts[application_status] += 1

        # Monthly application trends
        if application.application_date:
            month = application.application_date.strftime("%Y-%m")
            monthly_counts[month] += 1

        # Company-wise analysis
        company_counts[company_name]["applications"] += 1

        if application_status == "Interview":
            company_counts[company_name]["interviews"] += 1

        elif application_status == "Selected":
            company_counts[company_name]["offers"] += 1

        elif application_status == "Rejected":
            company_counts[company_name]["rejections"] += 1

    interview_count = status_counts["Interview"]
    offer_count = status_counts["Selected"]
    rejection_count = status_counts["Rejected"]
    assessment_count = status_counts["Assessment"]

    # Existing interview conversion calculation
    interview_conversion_rate = (
        round((interview_count / total_applications) * 100, 2)
        if total_applications > 0 else 0
    )

    # Offer conversion rate
    offer_conversion_rate = (
        round((offer_count / total_applications) * 100, 2)
        if total_applications > 0 else 0
    )

    # Applications that progressed beyond the Applied stage
    progressed_applications = (
        assessment_count + interview_count + offer_count
    )

    progression_rate = (
        round((progressed_applications / total_applications) * 100, 2)
        if total_applications > 0 else 0
    )

    # Monthly trend
    monthly_trend = [
        {
            "month": month,
            "applications": count
        }
        for month, count in sorted(monthly_counts.items())
    ]

    # Company-wise breakdown
    company_breakdown = [
        {
            "company": company,
            **details
        }
        for company, details in sorted(
            company_counts.items(),
            key=lambda item: item[1]["applications"],
            reverse=True
        )
    ]

    return {
        "total_applications": total_applications,
        "interviews": interview_count,
        "offers": offer_count,
        "rejections": rejection_count,
        "assessments": assessment_count,
        "interview_conversion_rate": interview_conversion_rate,
        "offer_conversion_rate": offer_conversion_rate,
        "progression_rate": progression_rate,
        "status_breakdown": status_counts,
        "monthly_trend": monthly_trend,
        "company_breakdown": company_breakdown
    }


# UPDATE A JOB APPLICATION
@router.put(
    "/{application_id}",
    response_model=JobApplicationResponse
)
def update_application(
    application_id: int,
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    application.company_name = application_data.company_name
    application.job_role = application_data.job_role
    application.status = application_data.status
    application.application_date = application_data.application_date
    application.job_description = application_data.job_description

    db.commit()
    db.refresh(application)

    return application


# DELETE A JOB APPLICATION
@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return {"message": "Application deleted successfully"}
