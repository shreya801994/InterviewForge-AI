from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models import InterviewSession, SkillScore, Report

class DashboardService:
    @staticmethod
    def get_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Aggregates key interview statistics for the authenticated user.
        Returns total interviews, average score, strong/weak topics, latest score, and score trend.
        """
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "COMPLETED"
        ).order_by(InterviewSession.completed_at.asc()).all()

        # 1. Aggregate from sessions and reports
        total_interviews = len(sessions)
        
        # Pull score from report if available, else average_score. Multiply by 10 to convert from 10-point scale to 100%.
        scores = []
        for s in sessions:
            if s.report and s.report.overall_score is not None:
                scores.append(s.report.overall_score * 10.0)
            elif s.average_score is not None:
                scores.append(s.average_score * 10.0)

        overall_avg = round(sum(scores) / len(scores), 2) if scores else 0.0
        latest_score = round(scores[-1], 2) if scores else 0.0

        # Build chronological score trend
        score_trend = [
            {"attempt": idx + 1, "score": round(s, 2)}
            for idx, s in enumerate(scores)
        ]

        # Fetch skill scores for topic analysis
        skill_scores = db.query(SkillScore).filter(
            SkillScore.user_id == user_id
        ).all()

        # Sort by overall_avg descending for strong, ascending for weak
        sorted_skills = sorted(skill_scores, key=lambda x: x.overall_avg or 0.0, reverse=True)

        strong_topics = [
            {"topic": s.skill_name, "score": round((s.overall_avg or 0.0) * 10.0, 2)}
            for s in sorted_skills[:5] if s.overall_avg
        ]
        weak_topics = [
            {"topic": s.skill_name, "score": round((s.overall_avg or 0.0) * 10.0, 2)}
            for s in reversed(sorted_skills[-5:]) if s.overall_avg
        ]

        return {
            "total_interviews": total_interviews,
            "average_score": overall_avg,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "latest_score": latest_score,
            "score_trend": score_trend
        }

    @staticmethod
    def get_history(db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Returns a list of completed interview sessions for the user, with score and date.
        """
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "COMPLETED"
        ).order_by(InterviewSession.completed_at.desc()).all()

        history = []
        for s in sessions:
            score = 0.0
            if s.report and s.report.overall_score is not None:
                score = s.report.overall_score * 10.0
            elif s.average_score is not None:
                score = s.average_score * 10.0
                
            history.append({
                "id": s.id,
                "date": s.completed_at.isoformat() if s.completed_at else None,
                "role": s.role,
                "difficulty": s.difficulty,
                "score": round(score, 2),
                "questions_answered": s.questions_answered,
                "completion_percentage": round(s.completion_percentage or 0.0, 1),
            })
            
        return history

    @staticmethod
    def get_report(db: Session, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Returns the generated report for a completed interview session.
        Verifies user ownership before returning.
        """
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        ).first()

        if not session:
            return None

        report = db.query(Report).filter(Report.session_id == session_id).first()
        if not report:
            return None

        return {
            "session_id": session_id,
            "role": session.role,
            "difficulty": session.difficulty,
            "overall_score": report.overall_score or 0.0,
            "strengths": report.strengths or [],
            "weaknesses": report.weaknesses or [],
            "summary": report.summary or "",
            "roadmap": report.roadmap or [],
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "report_version": report.report_version or "1.0",
        }
