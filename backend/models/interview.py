from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class InterviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class Question(BaseModel):
    id: str = Field(..., alias="_id")
    text: str
    type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    points: int = 1

class InterviewBase(BaseModel):
    job_id: str
    candidate_id: str
    recruiter_id: str
    status: InterviewStatus = InterviewStatus.PENDING
    scheduled_at: Optional[datetime] = None
    duration_minutes: int = 30
    total_questions: int = 10

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    status: Optional[InterviewStatus] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    total_questions: Optional[int] = None

class InterviewInDB(InterviewBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    questions: List[Question] = []
    answers: Dict[str, str] = {}  # question_id: answer
    score: Optional[float] = None
    feedback: Optional[str] = None
    ai_generated_questions: bool = False

class InterviewResponse(InterviewBase):
    id: str
    created_at: datetime
    updated_at: datetime
    score: Optional[float] = None
    feedback: Optional[str] = None

class InterviewSubmission(BaseModel):
    interview_id: str
    answers: Dict[str, str]  # question_id: answer

class InterviewResult(BaseModel):
    interview_id: str
    score: float
    feedback: str
    completed_at: datetime = Field(default_factory=datetime.utcnow) 