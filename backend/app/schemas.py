from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# Base User Schema
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="The full name of the user")
    email: EmailStr = Field(..., description="A valid email address")

# Schema for User Registration
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Password must be at least 6 characters")

# Schema for User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for User Response
class UserResponse(UserBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# JWT Token Response
class Token(BaseModel):
    access_token: str
    token_type: str

# Token Data embedded inside JWT
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None

# --- Phase 2: Resume Schemas ---

class ATSSchema(BaseModel):
    ats_score: int
    ats_breakdown: str
    ats_suggestions: List[str]

class ProjectEvaluationSchema(BaseModel):
    evaluation: str

class BaseResumeAnalysisSchema(BaseModel):
    skills: List[str] = Field(default_factory=list, description="Extracted skills list")
    projects: List[str] = Field(default_factory=list, description="Extracted project names list")
    strengths: List[str] = Field(default_factory=list, description="Extracted candidate strengths")
    focus_areas: List[str] = Field(default_factory=list, description="Recommended focus/study areas")

class ResumeAnalysisSchema(BaseResumeAnalysisSchema):
    ats_score: Optional[int] = Field(None, description="Heuristic ATS readiness score 0-100")
    ats_breakdown: Optional[str] = Field(None, description="Explanation of ATS score")
    ats_suggestions: List[str] = Field(default_factory=list, description="Suggestions to improve ATS readiness")

class ResumeUploadResponse(BaseModel):
    message: str
    resume_id: str
    analysis: ResumeAnalysisSchema

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    parsed_text: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    ats_score: Optional[int] = None
    ats_breakdown: Optional[str] = None
    ats_suggestions: List[str] = Field(default_factory=list)
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Phase 3: Interview Engine Schemas ---

class InterviewStartRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=100, description="The job role, e.g. Software Engineer")
    difficulty: str = Field(..., min_length=1, max_length=50, description="Difficulty: Easy, Medium, Hard")
    question_count: int = Field(10, description="Number of questions in the interview")
    focus_topics: List[str] = Field(default_factory=list, description="Topics to focus on")
    resume_id: Optional[str] = Field(None, description="Optional associated resume ID")
    job_description: Optional[str] = Field(None, description="Optional job description for tailored questions")

class InterviewStartResponse(BaseModel):
    session_id: str
    first_question: str
    first_question_type: str = "conceptual"
    first_question_time_limit: Optional[int] = None
    status: str

class AnswerSubmissionRequest(BaseModel):
    answer_text: str = Field(..., min_length=1, description="Candidate's technical answer")

class EvaluationDetailSchema(BaseModel):
    technical_accuracy: float = Field(..., ge=0, le=10, description="Score 0-10 on correctness")
    communication: float = Field(..., ge=0, le=10, description="Score 0-10 on communication style")
    depth: float = Field(..., ge=0, le=10, description="Score 0-10 on coverage depth")
    feedback: str = Field(..., description="General feedback message")

class AnswerSubmissionResponse(BaseModel):
    evaluation: EvaluationDetailSchema
    next_question: Optional[str] = None
    next_question_type: Optional[str] = None
    next_question_time_limit: Optional[int] = None
    is_completed: bool

class MessageResponse(BaseModel):
    id: str
    message_type: str
    content: str
    question_type: Optional[str] = None
    time_limit_seconds: Optional[int] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionDetailsResponse(BaseModel):
    id: str
    role: str
    difficulty: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None
    questions_answered: int = 0
    average_score: Optional[float] = None
    completion_percentage: float = 0.0
    messages: List[MessageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
