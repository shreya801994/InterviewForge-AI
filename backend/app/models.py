import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    skill_scores = relationship("SkillScore", back_populates="user", cascade="all, delete-orphan")


from sqlalchemy import UniqueConstraint

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    parsed_text = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)       # Stores list of skills: []
    projects = Column(JSON, nullable=True)     # Stores list of projects: []
    strengths = Column(JSON, nullable=True)    # Stores list of strengths: []
    focus_areas = Column(JSON, nullable=True)  # Stores list of focus_areas: []
    ats_score = Column(Integer, nullable=True)
    ats_breakdown = Column(Text, nullable=True)
    ats_suggestions = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="resumes")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(String(100), nullable=False)
    job_description = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="CREATED")  # CREATED, ACTIVE, EVALUATING, COMPLETED
    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    question_count = Column(Integer, default=3)
    focus_topics = Column(JSON, nullable=True)
    
    # Metrics
    questions_answered = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    completion_percentage = Column(Float, default=0.0)

    # Anti-Cheat
    violation_count = Column(Integer, default=0)
    terminated_for_violation = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    messages = relationship("InterviewMessage", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", uselist=False, back_populates="session", cascade="all, delete-orphan")


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    message_type = Column(String(20), nullable=False)  # QUESTION, ANSWER, FEEDBACK
    content = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True, default="conceptual")
    time_limit_seconds = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    question_id = Column(String(36), ForeignKey("question_bank.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="messages")
    question = relationship("QuestionBank")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), index=True, unique=True, nullable=False)
    overall_score = Column(Float, nullable=True)
    strengths = Column(JSON, nullable=True)      # JSON list
    weaknesses = Column(JSON, nullable=True)     # JSON list
    summary = Column(Text, nullable=True)
    consistency_feedback = Column(Text, nullable=True)
    roadmap = Column(JSON, nullable=True)        # JSON roadmap structure
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    report_version = Column(String(50), default="1.0")

    # Relationships
    session = relationship("InterviewSession", back_populates="report")


class SkillScore(Base):
    __tablename__ = "skill_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_name = Column(String(100), nullable=False)
    
    technical_avg = Column(Float, default=0.0)
    communication_avg = Column(Float, default=0.0)
    depth_avg = Column(Float, default=0.0)
    overall_avg = Column(Float, default=0.0)
    attempt_count = Column(Integer, default=0)
    last_score = Column(Float, default=0.0)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'skill_name', name='uq_user_skill'),
    )

    # Relationships
    user = relationship("User", back_populates="skill_scores")


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(100), nullable=False)       # e.g., "DSA", "DBMS", "OS", "OOP"
    topic = Column(String(100), nullable=False)          # e.g., "Arrays", "Graphs", etc.
    difficulty = Column(String(50), nullable=False)      # e.g., "Easy", "Medium", "Hard"
    question_type = Column(String(50), nullable=False, server_default="conceptual") # "conceptual" or "coding"
    time_limit_seconds = Column(Integer, nullable=True)  # e.g., 180
    question_text = Column(Text, nullable=False)
    expected_keywords = Column(JSON, nullable=False)     # List of expected keywords: ["keyword1", "keyword2"]
