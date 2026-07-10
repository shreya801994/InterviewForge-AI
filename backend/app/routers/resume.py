from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import ResumeUploadResponse, ResumeResponse, ResumeAnalysisSchema
from app.services.resume_service import ResumeService
from app.routers.auth import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/resume", tags=["Resumes"])

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated route to upload a PDF resume, analyze contents via Gemini, and store structured metadata.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected for upload."
        )

    # 1. Preliminary check on Content-Length header (to avoid reading giant payloads)
    from app.config import settings
    max_size_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    content_length = file.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uploaded file size exceeds the maximum limit of {settings.MAX_PDF_SIZE_MB}MB."
                )
        except ValueError:
            pass

    # 2. Check file extension before reading
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF resumes are supported."
        )

    # Read the file bytes directly into memory
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to read uploaded file contents: {str(e)}"
        )

    # 3. Post-read check of actual size of stream
    if len(file_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file size exceeds the maximum limit of {settings.MAX_PDF_SIZE_MB}MB."
        )


    # Hand off to the resume service coordinator
    db_resume = ResumeService.process_and_save_resume(
        db=db,
        user_id=current_user.id,
        file_bytes=file_bytes,
        filename=file.filename
    )

    # Build response schemas
    analysis = ResumeAnalysisSchema(
        skills=db_resume.skills or [],
        projects=db_resume.projects or [],
        strengths=db_resume.strengths or [],
        focus_areas=db_resume.focus_areas or [],
        ats_score=db_resume.ats_score,
        ats_breakdown=db_resume.ats_breakdown,
        ats_suggestions=db_resume.ats_suggestions or []
    )

    return ResumeUploadResponse(
        message="Resume uploaded successfully",
        resume_id=db_resume.id,
        analysis=analysis
    )


@router.get("/latest", response_model=ResumeResponse)
def get_latest_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated route to retrieve the latest uploaded resume metadata for the user.
    """
    db_resume = ResumeService.get_latest_resume(db, current_user.id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload a resume first."
        )
    return db_resume
