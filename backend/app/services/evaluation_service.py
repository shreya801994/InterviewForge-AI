from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
import logging
import json

from app.models import SkillScore, Report, InterviewSession, InterviewMessage, Resume
from app.ai.client import AIClient
from app.ai.prompts import ANSWER_EVALUATION_PROMPT, INTERVIEW_REPORT_PROMPT
from app.schemas import EvaluationDetailSchema
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EvaluationService:

    @staticmethod
    def evaluate_answer(
        question_text: str, 
        expected_keywords: list, 
        user_answer: str
    ) -> dict:
        """
        Sends the candidate's answer to the Gemini API to grade it based on accuracy, 
        communication style, and depth. Returns grading scores and feedback text.
        """
        prompt = ANSWER_EVALUATION_PROMPT.format(
            question_text=question_text,
            expected_keywords=", ".join(expected_keywords),
            user_answer=user_answer
        )
        
        try:
            parsed_eval = AIClient.generate(prompt=prompt, schema=EvaluationDetailSchema)
            
            return {
                "technical_accuracy": float(parsed_eval.technical_accuracy),
                "communication": float(parsed_eval.communication),
                "depth": float(parsed_eval.depth),
                "feedback": str(parsed_eval.feedback)
            }
        except Exception:
            logger.exception("Gemini grading request failed")

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI grading service temporarily unavailable."
            )


    @staticmethod
    def record_skill_score(
        db: Session, 
        user_id: str, 
        skill_name: str, 
        evaluation: dict
    ) -> SkillScore:
        """
        Updates the skill_scores table using rolling averages based on the evaluation detail.
        """
        # Convert 0-10 scores to a 0-100 percentage scale
        tech_score = min(max(evaluation["technical_accuracy"] * 10.0, 0.0), 100.0)
        comm_score = min(max(evaluation["communication"] * 10.0, 0.0), 100.0)
        depth_score = min(max(evaluation["depth"] * 10.0, 0.0), 100.0)
        
        overall = (tech_score + comm_score + depth_score) / 3.0

        db_score = db.query(SkillScore).filter(
            SkillScore.user_id == user_id,
            SkillScore.skill_name == skill_name
        ).first()

        if not db_score:
            db_score = SkillScore(
                user_id=user_id,
                skill_name=skill_name,
                technical_avg=tech_score,
                communication_avg=comm_score,
                depth_avg=depth_score,
                overall_avg=overall,
                attempt_count=1,
                last_score=overall
            )
            db.add(db_score)
        else:
            # Update rolling averages
            n = db_score.attempt_count
            db_score.technical_avg = ((db_score.technical_avg * n) + tech_score) / (n + 1)
            db_score.communication_avg = ((db_score.communication_avg * n) + comm_score) / (n + 1)
            db_score.depth_avg = ((db_score.depth_avg * n) + depth_score) / (n + 1)
            db_score.overall_avg = ((db_score.overall_avg * n) + overall) / (n + 1)
            db_score.attempt_count += 1
            db_score.last_score = overall

        try:
            db.commit()
            db.refresh(db_score)
            return db_score
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error writing skill score record: {str(e)}"
            )

    @staticmethod
    def generate_interview_report(db: Session, session_id: str) -> Report:
        """
        Generates a comprehensive interview report using Gemini based on the session transcript.
        """
        session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            return None

        messages = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id
        ).order_by(InterviewMessage.created_at.asc()).all()

        transcript = ""
        for m in messages:
            transcript += f"[{m.message_type}]: {m.content}\n"
            if m.message_type == "ANSWER" and m.feedback:
                try:
                    fb = json.loads(m.feedback)
                    transcript += f"[EVALUATION]: Accuracy: {fb.get('technical_accuracy', 0)}, Depth: {fb.get('depth', 0)}, Comm: {fb.get('communication', 0)}\n"
                    transcript += f"[FEEDBACK]: {fb.get('feedback', '')}\n"
                except Exception:
                    pass

        resume_context_str = "No resume provided."
        resume = db.query(Resume).filter(Resume.user_id == session.user_id).order_by(Resume.uploaded_at.desc()).first()
        if resume:
            resume_context_str = f"Skills: {', '.join(resume.skills or [])}. Projects: {', '.join(resume.projects or [])}. Strengths: {', '.join(resume.strengths or [])}"

        prompt = INTERVIEW_REPORT_PROMPT.format(
            role=session.role,
            difficulty=session.difficulty,
            resume_context=resume_context_str,
            transcript=transcript
        )
        
        try:
            class ReportOutput(BaseModel):
                overall_score: float
                strengths: list[str]
                weaknesses: list[str]
                summary: str
                consistency_feedback: str
                roadmap: list[str]
            
            parsed_report = AIClient.generate(prompt=prompt, schema=ReportOutput)
            
            # Retrieve overall score
            overall_score = float(parsed_report.overall_score)

            report = Report(
                session_id=session_id,
                overall_score=overall_score,
                strengths=parsed_report.strengths,
                weaknesses=parsed_report.weaknesses,
                summary=parsed_report.summary,
                consistency_feedback=parsed_report.consistency_feedback,
                roadmap=parsed_report.roadmap
            )
            
            # Remove any old report to replace it if re-generating
            existing = db.query(Report).filter(Report.session_id == session_id).first()
            if existing:
                db.delete(existing)
                
            db.add(report)
            db.commit()
            db.refresh(report)
            return report

        except Exception as e:
            
            logger.exception("Interview Report generation failed")
            db.rollback()
            return None
