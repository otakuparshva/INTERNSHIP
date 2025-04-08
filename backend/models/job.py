from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"

class JobBase(BaseModel):
    title: str
    description: str
    requirements: List[str]
    status: JobStatus = JobStatus.OPEN
    recruiter_id: str

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    status: Optional[JobStatus] = None

class JobInDB(JobBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ai_generated_description: Optional[str] = None
    total_applications: int = 0
    total_interviews: int = 0

class JobResponse(JobBase):
    id: str
    created_at: datetime
    updated_at: datetime
    total_applications: int
    total_interviews: int

class JobSearch(BaseModel):
    query: Optional[str] = None
    status: Optional[JobStatus] = None
    recruiter_id: Optional[str] = None
    page: int = 1
    limit: int = 10

class JobApplication(BaseModel):
    job_id: str
    candidate_id: str
    resume_url: str
    cover_letter: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ai_score: Optional[float] = None
    ai_summary: Optional[str] = None 