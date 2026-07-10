from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.dashboard_service import DashboardService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated statistics: total interviews, average score, score trend,
    strong topics, and weak topics for the current user.
    """
    return DashboardService.get_stats(db, current_user.id)


@router.get("/history")
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of completed interview sessions with date, role, and score.
    """
    return DashboardService.get_history(db, current_user.id)


@router.get("/report/{session_id}")
def get_interview_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the full AI-generated report for a specific completed interview session.
    """
    report = DashboardService.get_report(db, session_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this session."
        )
    return report
