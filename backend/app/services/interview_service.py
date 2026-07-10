from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import json
from typing import Optional, List

from app.models import InterviewSession, InterviewMessage, QuestionBank, Resume, SkillScore
from app.services.question_bank_service import QuestionBankService
from app.services.evaluation_service import EvaluationService

class InterviewService:
    @staticmethod
    def start_interview(
        db: Session, 
        user_id: str, 
        role: str, 
        difficulty: str, 
        question_count: int = 3,
        focus_topics: List[str] = None,
        resume_id: Optional[str] = None
    ) -> InterviewSession:
        """
        Creates a new interview session and selects the first question.
        Follows priority: Resume Projects > Resume Skills > Resume Focus Areas > Question Bank.
        """
        if focus_topics is None:
            focus_topics = []

        # 1. Create the session
        session = InterviewSession(
            user_id=user_id,
            role=role,
            difficulty=difficulty,
            question_count=question_count,
            focus_topics=focus_topics,
            status="CREATED",
            started_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 2. Build ordered priority terms
        priority_terms = []
        if focus_topics:
            priority_terms.extend(focus_topics)

        if resume_id:
            resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
            if resume:
                if resume.projects:
                    priority_terms.extend(resume.projects)
                if resume.skills:
                    priority_terms.extend(resume.skills)
                if resume.focus_areas:
                    priority_terms.extend(resume.focus_areas)

        priority_terms_lower = [str(t).lower() for t in priority_terms]
        
        first_question = None
        
        # 2a. Try AI Generation First
        resume_context_str = ""
        if resume_id and resume:
            resume_context_str = f"Skills: {', '.join(resume.skills or [])}. Strengths: {', '.join(resume.strengths or [])}"

        try:
            from app.ai.client import AIClient
            from app.ai.prompts import PROMPT_GENERATE_QUESTION
            from pydantic import BaseModel
            
            class GenQuestion(BaseModel):
                question_text: str
                expected_keywords: List[str]

            prompt = PROMPT_GENERATE_QUESTION.format(
                role=role,
                difficulty=difficulty,
                job_description=session.job_description or "None provided",
                resume_context=resume_context_str or "None provided",
                previous_questions="None"
            )
            generated = AIClient.generate(prompt=prompt, schema=GenQuestion)
            
            new_qb = QuestionBank(
                category="AI Generated",
                topic=role,
                difficulty=difficulty,
                question_text=generated.question_text,
                expected_keywords=generated.expected_keywords
            )
            db.add(new_qb)
            db.commit()
            first_question = new_qb
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("AI generation failed for first question", exc_info=True)
            pass # Silently fallback
            
        # 2b. Fallback to static selection
        if not first_question:
            all_questions = QuestionBankService.get_questions(db, difficulty=difficulty)

            for term in priority_terms_lower:
                matched_questions = []
                for q in all_questions:
                    if term in q.topic.lower() or term in q.category.lower() or term in q.question_text.lower():
                        matched_questions.append(q)
                
                if matched_questions:
                    import random
                    first_question = random.choice(matched_questions)
                    break

            if not first_question:
                first_question = QuestionBankService.get_random_question(db, difficulty=difficulty)

            if not first_question:
                first_question = QuestionBankService.get_random_question(db)

            if not first_question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No questions available in the question bank to start the interview."
                )

        # 3. Save the first question message
        question_msg = InterviewMessage(
            session_id=session.id,
            message_type="QUESTION",
            content=first_question.question_text,
            question_type=first_question.question_type,
            time_limit_seconds=first_question.time_limit_seconds
        )
        db.add(question_msg)

        # 4. Transition session status to ACTIVE
        session.status = "ACTIVE"
        db.commit()
        db.refresh(session)

        # We need to temporarily attach these to the session so the router can extract them
        session.first_question_type = first_question.question_type
        session.first_question_time_limit = first_question.time_limit_seconds

        return session

    @staticmethod
    def get_session_details(db: Session, session_id: str, user_id: str) -> InterviewSession:
        """
        Retrieves interview session details along with message history.
        Verifies user ownership to prevent unauthorized data exposure.
        """
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found."
            )

        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this interview session."
            )

        session.messages = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id
        ).order_by(
            InterviewMessage.created_at.asc()
        ).all()

        return session

    @staticmethod
    def submit_answer(
        db: Session, 
        session_id: str, 
        user_id: str, 
        answer_text: str
    ) -> dict:
        """
        Submits candidate answer, performs Gemini grading, updates user skill scores,
        updates session metrics, and generates the next adaptive question or completes the interview.
        """
        # 1. Fetch and validate session
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found."
            )

        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this interview session."
            )

        if session.terminated_for_violation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This session has been terminated due to anti-cheat violations."
            )

        if session.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit answer. Session is currently in {session.status} state."
            )

        # 2. Get the last active question
        last_question = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id,
            InterviewMessage.message_type == "QUESTION"
        ).order_by(
            InterviewMessage.created_at.desc()
        ).first()

        if not last_question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inconsistent state: No active question found for this session."
            )

        session.status = "EVALUATING"
        db.commit()

        # 3. Resolve topic and expected keywords from question bank
        q_bank_item = db.query(QuestionBank).filter(
            QuestionBank.question_text == last_question.content
        ).first()

        topic = "General"
        expected_keywords = []
        if q_bank_item:
            topic = q_bank_item.topic
            expected_keywords = q_bank_item.expected_keywords or []

        # 4. Evaluate using Gemini
        evaluation = EvaluationService.evaluate_answer(
            question_text=last_question.content,
            expected_keywords=expected_keywords,
            user_answer=answer_text
        )

        # 5. Save the answer message and feedback metrics
        avg_score = (
            evaluation["technical_accuracy"] + 
            evaluation["communication"] + 
            evaluation["depth"]
        ) / 3.0

        answer_msg = InterviewMessage(
            session_id=session_id,
            message_type="ANSWER",
            content=answer_text,
            score=avg_score,
            feedback=json.dumps(evaluation)
        )
        db.add(answer_msg)

        # 6. Record skill score using rolling averages
        EvaluationService.record_skill_score(
            db=db,
            user_id=user_id,
            skill_name=topic,
            evaluation=evaluation
        )

        # 7. Update Session Metrics
        session.questions_answered += 1
        
        # Calculate overall session average
        all_answers = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id,
            InterviewMessage.message_type == "ANSWER"
        ).all()
        
        total_score = sum([a.score for a in all_answers]) if all_answers else 0.0
        session.average_score = (total_score / len(all_answers)) if all_answers else 0.0
        
        # Safe completion percentage
        target = session.question_count if session.question_count > 0 else 1
        session.completion_percentage = min((session.questions_answered / target) * 100.0, 100.0)
        
        db.commit()

        # 8. Check Deterministic Completion
        if session.questions_answered >= session.question_count:
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            
            # Generate final report
            EvaluationService.generate_interview_report(db, session.id)
            
            return {
                "evaluation": evaluation,
                "next_question": None,
                "is_completed": True
            }

        # 9. Adaptive Question Selection for follow-up
        asked_questions = db.query(InterviewMessage).filter(
            InterviewMessage.session_id == session_id,
            InterviewMessage.message_type == "QUESTION"
        ).all()
        asked_texts = [q.content for q in asked_questions]
        
        q_bank_asked = db.query(QuestionBank).filter(
            QuestionBank.question_text.in_(asked_texts)
        ).all()
        exclude_ids = [q.id for q in q_bank_asked]

        # 9a. Try AI Generation First
        try:
            from app.ai.client import AIClient
            from app.ai.prompts import PROMPT_GENERATE_QUESTION
            from pydantic import BaseModel
            
            class GenQuestion(BaseModel):
                question_text: str
                expected_keywords: List[str]

            resume_context_str = ""
            resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).first()
            if resume:
                resume_context_str = f"Skills: {', '.join(resume.skills or [])}. Strengths: {', '.join(resume.strengths or [])}"

            prompt = PROMPT_GENERATE_QUESTION.format(
                role=session.role,
                difficulty=session.difficulty,
                job_description=session.job_description or "None provided",
                resume_context=resume_context_str or "None provided",
                previous_questions=", ".join(asked_texts)
            )
            generated = AIClient.generate(prompt=prompt, schema=GenQuestion)
            
            new_qb = QuestionBank(
                category="AI Generated",
                topic=session.role,
                difficulty=session.difficulty,
                question_text=generated.question_text,
                expected_keywords=generated.expected_keywords
            )
            db.add(new_qb)
            db.commit()
            next_q_bank_item = new_qb
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("AI generation failed for next question", exc_info=True)
            pass # Silently fallback

        # 9b. Fallback to static QuestionBank logic
        if not next_q_bank_item:
            if session.focus_topics:
                for ft in session.focus_topics:
                    next_q_bank_item = QuestionBankService.get_random_question(
                        db=db,
                        topic=ft,
                        difficulty=session.difficulty,
                        exclude_ids=exclude_ids
                    )
                    if next_q_bank_item:
                        break

            if not next_q_bank_item:
                # Fallback to weak topics
                distinct_topics = db.query(QuestionBank.topic).distinct().all()
                topics = [t[0] for t in distinct_topics]

                topic_scores = {}
                for t in topics:
                    score_record = db.query(SkillScore).filter(
                        SkillScore.user_id == user_id,
                        SkillScore.skill_name == t
                    ).order_by(SkillScore.last_updated.desc()).first()
                    topic_scores[t] = score_record.overall_avg if score_record else 0.0

                sorted_topics = sorted(topic_scores.keys(), key=lambda x: topic_scores[x])

                for t in sorted_topics:
                    next_q_bank_item = QuestionBankService.get_random_question(
                        db=db,
                        topic=t,
                        difficulty=session.difficulty,
                        exclude_ids=exclude_ids
                    )
                    if next_q_bank_item:
                        break

            # Fallbacks
            if not next_q_bank_item:
                next_q_bank_item = QuestionBankService.get_random_question(
                    db=db,
                    difficulty=session.difficulty,
                    exclude_ids=exclude_ids
                )

            if not next_q_bank_item:
                next_q_bank_item = QuestionBankService.get_random_question(
                    db=db,
                    exclude_ids=exclude_ids
                )

        if not next_q_bank_item:
            # Bank exhausted
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            EvaluationService.generate_interview_report(db, session.id)
            return {
                "evaluation": evaluation,
                "next_question": None,
                "is_completed": True
            }

        # Save next question
        next_question_msg = InterviewMessage(
            session_id=session_id,
            message_type="QUESTION",
            content=next_q_bank_item.question_text,
            question_type=next_q_bank_item.question_type,
            time_limit_seconds=next_q_bank_item.time_limit_seconds
        )
        db.add(next_question_msg)
        
        session.status = "ACTIVE"
        db.commit()

        return {
            "evaluation": evaluation,
            "next_question": next_q_bank_item.question_text,
            "next_question_type": next_q_bank_item.question_type,
            "next_question_time_limit": next_q_bank_item.time_limit_seconds,
            "is_completed": False
        }

    @staticmethod
    def terminate_session(db: Session, session_id: str, user_id: str):
        """
        Increments violation_count and force-terminates the session if count >= 2.
        """
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found.")
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not have access to this interview session.")

        session.violation_count = (session.violation_count or 0) + 1
        if session.violation_count >= 2:
            session.terminated_for_violation = True
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            
            # Generate final report since session is now complete
            EvaluationService.generate_interview_report(db, session.id)
        else:
            db.commit()
