from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_ping():
    """Liveness check for monitoring platforms."""
    return {"status": "healthy"}

@router.get("/health/detailed")
def detailed_health(db: Session = Depends(get_db)):
    """Detailed diagnostic health report for verification."""
    # Check Database connection
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # Check Gemini API Key configuration status
    gemini_status = "unavailable"
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
        gemini_status = "available"

    return {
        "database": db_status,
        "gemini": gemini_status,
        "version": "1.0.0"
    }
