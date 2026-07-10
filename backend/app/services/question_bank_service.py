from sqlalchemy.orm import Session
from typing import List, Optional
import random

from app.models import QuestionBank

class QuestionBankService:
    @staticmethod
    def get_questions(
        db: Session,
        category: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[QuestionBank]:
        """
        Retrieves all questions from the bank, applying filters for category, topic, or difficulty if specified.
        """
        query = db.query(QuestionBank)
        if category:
            query = query.filter(QuestionBank.category == category)
        if topic:
            query = query.filter(QuestionBank.topic == topic)
        if difficulty:
            query = query.filter(QuestionBank.difficulty == difficulty)
        return query.all()

    @staticmethod
    def get_random_question(
        db: Session,
        category: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> Optional[QuestionBank]:
        """
        Retrieves a single random question matching criteria, optionally excluding certain IDs.
        """
        questions = QuestionBankService.get_questions(db, category, topic, difficulty)
        
        if exclude_ids:
            questions = [q for q in questions if q.id not in exclude_ids]
            
        if not questions:
            # Try to relax the difficulty filter first if no questions are found
            if difficulty:
                questions = QuestionBankService.get_questions(db, category, topic, None)
                if exclude_ids:
                    questions = [q for q in questions if q.id not in exclude_ids]
                    
            if not questions:
                return None
                
        return random.choice(questions)
