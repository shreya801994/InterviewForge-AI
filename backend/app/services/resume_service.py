from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.models import Resume
from app.services.pdf_service import PdfService
from app.ai.client import AIClient
from app.schemas import BaseResumeAnalysisSchema, ResumeAnalysisSchema, ProjectEvaluationSchema, ATSSchema
from app.ai.prompts import RESUME_ANALYSIS_PROMPT, PROMPT_EVALUATE_PROJECT, PROMPT_ATS_SCORE
import re
import requests
import base64
import logging

class ResumeService:
    @staticmethod
    def process_and_save_resume(
        db: Session, 
        user_id: str, 
        file_bytes: bytes, 
        filename: str
    ) -> Resume:
        """
        Orchestrates resume text extraction, Gemini AI parser, and database transaction.
        """
        # 1. Parse text from PDF
        parsed_text = PdfService.validate_and_extract(file_bytes, filename)

        # 2. Extract skills, projects, strengths, focus areas via Gemini
        prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=parsed_text)
        analysis_obj = AIClient.generate(prompt=prompt, schema=BaseResumeAnalysisSchema)
        analysis = analysis_obj.model_dump()

        # 2b. Extract GitHub URLs and evaluate projects
        github_urls = re.findall(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", parsed_text)
        unique_repos = set()
        for repo in github_urls:
            clean_repo = repo.strip("/.").lower()
            if clean_repo.count("/") == 1:
                unique_repos.add(clean_repo)

        for repo in list(unique_repos)[:3]:  # Limit to 3 projects
            try:
                response = requests.get(f"https://api.github.com/repos/{repo}/readme", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    content_b64 = data.get("content", "")
                    if content_b64:
                        readme_text = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                        prompt_eval = PROMPT_EVALUATE_PROJECT.format(
                            github_url=f"https://github.com/{repo}", 
                            readme_content=readme_text[:3000]
                        )
                        proj_eval_obj = AIClient.generate(prompt=prompt_eval, schema=ProjectEvaluationSchema)
                        analysis["projects"].append(f"GitHub repo {repo}: {proj_eval_obj.evaluation}")
                elif response.status_code == 403:
                    logging.warning(f"GitHub API rate limit hit when fetching README for {repo}")
                    analysis["projects"].append(f"GitHub repo {repo}: Project analysis unavailable (rate limit)")
                elif response.status_code == 404:
                    analysis["projects"].append(f"GitHub repo {repo}: Project analysis unavailable (not found)")
            except Exception as e:
                logging.warning(f"Failed to fetch or evaluate README for {repo}: {e}")
                analysis["projects"].append(f"GitHub repo {repo}: Project analysis unavailable ({e})")

        # 2c. ATS Score evaluation
        try:
            ats_prompt = PROMPT_ATS_SCORE.format(resume_text=parsed_text)
            ats_obj = AIClient.generate(prompt=ats_prompt, schema=ATSSchema)
            ats_data = ats_obj.model_dump()
        except Exception as e:
            logging.warning(f"Failed to generate ATS score: {e}")
            ats_data = {
                "ats_score": None,
                "ats_breakdown": "ATS scoring unavailable at this time.",
                "ats_suggestions": []
            }

        # 3. Create database entity
        db_resume = Resume(
            user_id=user_id,
            parsed_text=parsed_text,
            skills=analysis["skills"],
            projects=analysis["projects"],
            strengths=analysis["strengths"],
            focus_areas=analysis["focus_areas"],
            ats_score=ats_data.get("ats_score"),
            ats_breakdown=ats_data.get("ats_breakdown"),
            ats_suggestions=ats_data.get("ats_suggestions", [])
        )

        try:
            db.add(db_resume)
            db.commit()
            db.refresh(db_resume)
            return db_resume
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database transaction failed while saving resume record: {str(e)}"
            )

    @staticmethod
    def get_latest_resume(db: Session, user_id: str) -> Optional[Resume]:
        """
        Queries the database for the user's most recently uploaded resume metadata.
        """
        try:
            return db.query(Resume).filter(
                Resume.user_id == user_id
            ).order_by(
                Resume.uploaded_at.desc()
            ).first()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database transaction failed while retrieving latest resume: {str(e)}"
            )
