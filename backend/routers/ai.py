from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.ai_models import AIModelHandler
from pydantic import BaseModel

router = APIRouter()
ai_handler = AIModelHandler()

class ResumeAnalysisRequest(BaseModel):
    resume_text: str

class JobDescriptionRequest(BaseModel):
    role: str
    requirements: List[str]

class InterviewQuestionsRequest(BaseModel):
    job_description: str
    num_questions: int = 5

@router.post("/analyze-resume")
async def analyze_resume(request: ResumeAnalysisRequest) -> Dict[str, Any]:
    try:
        analysis = await ai_handler.analyze_resume(request.resume_text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-job-description")
async def generate_job_description(request: JobDescriptionRequest) -> Dict[str, str]:
    try:
        description = await ai_handler.generate_job_description(
            request.role,
            request.requirements
        )
        return {"job_description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-interview-questions")
async def generate_interview_questions(request: InterviewQuestionsRequest) -> Dict[str, List[str]]:
    try:
        questions = await ai_handler.generate_interview_questions(
            request.job_description,
            request.num_questions
        )
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 