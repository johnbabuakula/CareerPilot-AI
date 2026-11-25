
import os
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends

from app.utils.skill_matcher import calculate_skill_match
from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.resume_parser import extract_text_from_pdf


router = APIRouter(
    prefix="/resume",
    tags=["Resume Analyzer"]
)


# PDF UPLOAD CONFIGURATION
MAX_PDF_SIZE = 5 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    temp_path = None

    try:
        # Validate file content type
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # Validate job description
        if not job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty."
            )

        # Validate filename
        filename = resume.filename or ""

        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a valid PDF file."
            )

        # Read PDF in chunks to control memory usage
        chunks = []
        total_size = 0

        while True:
            chunk = await resume.read(CHUNK_SIZE)

            if not chunk:
                break

            total_size += len(chunk)

            if total_size > MAX_PDF_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="PDF size must be less than 5 MB."
                )

            chunks.append(chunk)

        contents = b"".join(chunks)

        # Validate PDF signature
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid PDF."
            )

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # Extract PDF text
        resume_text = extract_text_from_pdf(temp_path)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        # Calculate skill match
        analysis_result = calculate_skill_match(
            resume_text,
            job_description
        )

        return {
            "message": "Resume analyzed successfully!",
            "user_id": current_user.id,
            "resume_text": resume_text,
            "job_description": job_description,
            "analysis": analysis_result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        # Remove temporary PDF file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        # Close uploaded file
        await resume.close()
