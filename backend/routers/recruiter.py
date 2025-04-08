from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
import json

from models.job import JobApplication
from models.interview import InterviewCreate, InterviewResponse, InterviewStatus
from models.user import UserResponse, UserRole
from routers.auth import get_current_recruiter, get_database

load_dotenv()

router = APIRouter()

# AI Service configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

async def generate_interview_questions(job_description: str, resume_text: str, num_questions: int = 10) -> List[dict]:
    """Generate interview questions using AI"""
    try:
        # Try Ollama first
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"Generate {num_questions} multiple choice interview questions based on this job description and resume. Job: {job_description[:1000]} Resume: {resume_text[:1000]}",
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response", "")
                    # Parse questions from response
                    questions = []
                    for q in response_text.split("\n\n"):
                        if "?" in q:
                            question_text = q.split("?")[0] + "?"
                            options = [opt.strip() for opt in q.split("?")[1].split("\n") if opt.strip()]
                            if len(options) >= 4:
                                questions.append({
                                    "text": question_text,
                                    "type": "multiple_choice",
                                    "options": options[:4],
                                    "correct_answer": options[0]  # Assuming first option is correct
                                })
                    return questions[:num_questions]
    except Exception as e:
        print(f"Ollama error: {str(e)}")
    
    # Fallback to Hugging Face
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={
                    "inputs": f"Generate {num_questions} multiple choice interview questions based on this job description and resume. Job: {job_description[:1000]} Resume: {resume_text[:1000]}",
                    "parameters": {
                        "max_length": 1000,
                        "temperature": 0.7
                    }
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result[0].get("generated_text", "")
                    # Parse questions from response
                    questions = []
                    for q in response_text.split("\n\n"):
                        if "?" in q:
                            question_text = q.split("?")[0] + "?"
                            options = [opt.strip() for opt in q.split("?")[1].split("\n") if opt.strip()]
                            if len(options) >= 4:
                                questions.append({
                                    "text": question_text,
                                    "type": "multiple_choice",
                                    "options": options[:4],
                                    "correct_answer": options[0]  # Assuming first option is correct
                                })
                    return questions[:num_questions]
    except Exception as e:
        print(f"Hugging Face error: {str(e)}")
    
    # Return default questions if AI fails
    return [
        {
            "text": "What is your greatest strength?",
            "type": "multiple_choice",
            "options": [
                "Problem-solving",
                "Communication",
                "Leadership",
                "Technical skills"
            ],
            "correct_answer": "Problem-solving"
        }
    ] * num_questions

@router.get("/applications")
async def get_applications(
    job_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {}
    
    # Get jobs posted by the recruiter
    recruiter_jobs = await db.jobs.find({"recruiter_id": current_user.id}).to_list(length=100)
    job_ids = [str(job["_id"]) for job in recruiter_jobs]
    query["job_id"] = {"$in": job_ids}
    
    if status:
        query["status"] = status
    
    cursor = db.applications.find(query)
    applications = await cursor.to_list(length=100)
    
    # Get job and candidate details for each application
    for app in applications:
        job = await db.jobs.find_one({"_id": ObjectId(app["job_id"])})
        if job:
            app["job"] = job
        
        candidate = await db.users.find_one({"_id": ObjectId(app["candidate_id"])})
        if candidate:
            app["candidate"] = {
                "id": str(candidate["_id"]),
                "email": candidate["email"],
                "full_name": candidate["full_name"]
            }
    
    return applications

@router.post("/applications/{application_id}/review")
async def review_application(
    application_id: str,
    status: str,
    feedback: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    application = await db.applications.find_one({"_id": ObjectId(application_id)})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if recruiter owns the job
    job = await db.jobs.find_one({"_id": ObjectId(application["job_id"])})
    if not job or job["recruiter_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update application status
    await db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {
            "$set": {
                "status": status,
                "feedback": feedback,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # TODO: Send email notification to candidate
    
    return {"message": "Application reviewed successfully"}

@router.post("/applications/{application_id}/schedule-interview")
async def schedule_interview(
    application_id: str,
    interview: InterviewCreate,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    application = await db.applications.find_one({"_id": ObjectId(application_id)})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if recruiter owns the job
    job = await db.jobs.find_one({"_id": ObjectId(application["job_id"])})
    if not job or job["recruiter_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get candidate's resume
    candidate = await db.candidates.find_one({"user_id": application["candidate_id"]})
    if not candidate or "resume_text" not in candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate resume not found"
        )
    
    # Generate interview questions
    questions = await generate_interview_questions(
        job["description"],
        candidate["resume_text"],
        interview.total_questions
    )
    
    # Create interview
    interview_dict = interview.dict()
    interview_dict["job_id"] = application["job_id"]
    interview_dict["candidate_id"] = application["candidate_id"]
    interview_dict["recruiter_id"] = current_user.id
    interview_dict["questions"] = questions
    interview_dict["created_at"] = datetime.utcnow()
    interview_dict["updated_at"] = datetime.utcnow()
    
    result = await db.interviews.insert_one(interview_dict)
    
    # Update application status
    await db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {
            "$set": {
                "status": "interview_scheduled",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Update job interview count
    await db.jobs.update_one(
        {"_id": ObjectId(application["job_id"])},
        {"$inc": {"total_interviews": 1}}
    )
    
    # TODO: Send email notification to candidate
    
    return {"message": "Interview scheduled successfully", "interview_id": str(result.inserted_id)}

@router.get("/interviews")
async def get_interviews(
    status: Optional[InterviewStatus] = None,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {"recruiter_id": current_user.id}
    if status:
        query["status"] = status
    
    cursor = db.interviews.find(query)
    interviews = await cursor.to_list(length=100)
    
    # Get job and candidate details for each interview
    for interview in interviews:
        job = await db.jobs.find_one({"_id": ObjectId(interview["job_id"])})
        if job:
            interview["job"] = job
        
        candidate = await db.users.find_one({"_id": ObjectId(interview["candidate_id"])})
        if candidate:
            interview["candidate"] = {
                "id": str(candidate["_id"]),
                "email": candidate["email"],
                "full_name": candidate["full_name"]
            }
    
    return interviews 