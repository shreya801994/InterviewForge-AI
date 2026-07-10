from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas import (
    InterviewStartRequest, 
    InterviewStartResponse, 
    AnswerSubmissionRequest, 
    AnswerSubmissionResponse, 
    SessionDetailsResponse
)
from app.services.interview_service import InterviewService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/interview", tags=["Interviews"])

@router.post("/start", response_model=InterviewStartResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def start_interview(
    request: Request,
    start_request: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Starts a new interview session for the authenticated user and generates the first question.
    """
    session = InterviewService.start_interview(
        db=db,
        user_id=current_user.id,
        role=start_request.role,
        difficulty=start_request.difficulty,
        question_count=start_request.question_count,
        focus_topics=start_request.focus_topics,
        resume_id=start_request.resume_id
    )

    # Fetch the first question from the session messages
    first_msg = session.messages[0] if session.messages else None
    
    # If messages are not populated, query for them
    if not first_msg:
        from app.models import InterviewMessage
        first_msg = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session.id,
            InterviewMessage.message_type == "QUESTION"
        ).first()

    first_question_text = first_msg.content if first_msg else ""
    
    q_type = getattr(session, "first_question_type", None)
    if not q_type and first_msg:
        q_type = getattr(first_msg, "question_type", "conceptual")
        
    t_limit = getattr(session, "first_question_time_limit", None)
    if not t_limit and first_msg:
        t_limit = getattr(first_msg, "time_limit_seconds", None)

    return InterviewStartResponse(
        session_id=session.id,
        first_question=first_question_text,
        first_question_type=q_type or "conceptual",
        first_question_time_limit=t_limit,
        status=session.status
    )


@router.get("/{session_id}", response_model=SessionDetailsResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the interview session details and full conversation history.
    """
    return InterviewService.get_session_details(db, session_id, current_user.id)


@router.post("/{session_id}/answer", response_model=AnswerSubmissionResponse)
@limiter.limit("30/minute")
def submit_answer(
    request: Request,
    session_id: str,
    answer_request: AnswerSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits an answer, executes Gemini grading, updates skill performance, and returns the next question.
    """
    result = InterviewService.submit_answer(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        answer_text=answer_request.answer_text
    )
    return result

@router.post("/{session_id}/terminate")
def terminate_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Terminates the session forcefully due to anti-cheat violations (e.g. tab switching).
    """
    InterviewService.terminate_session(db, session_id, current_user.id)
    return {"message": "Session terminated due to violation."}
