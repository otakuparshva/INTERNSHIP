from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import io

from models.job import JobApplication
from models.user import UserResponse, UserRole
from routers.auth import get_current_user, get_database

load_dotenv()

router = APIRouter()

# AI Service configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

async def analyze_resume_with_ai(resume_text: str, job_description: str) -> tuple:
    """Analyze resume using AI and return score and summary"""
    try:
        # Try Ollama first
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"Analyze this resume against the job description and provide a score (0-100) and a brief summary. Resume: {resume_text[:1000]} Job Description: {job_description[:1000]}",
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response", "")
                    # Parse score and summary from response
                    try:
                        score = float(response_text.split("Score:")[1].split()[0])
                        summary = response_text.split("Summary:")[1].strip()
                        return score, summary
                    except:
                        pass
    except Exception as e:
        print(f"Ollama error: {str(e)}")
    
    # Fallback to Hugging Face
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={
                    "inputs": f"Analyze this resume against the job description and provide a score (0-100) and a brief summary. Resume: {resume_text[:1000]} Job Description: {job_description[:1000]}",
                    "parameters": {
                        "max_length": 500,
                        "temperature": 0.7
                    }
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result[0].get("generated_text", "")
                    try:
                        score = float(response_text.split("Score:")[1].split()[0])
                        summary = response_text.split("Summary:")[1].strip()
                        return score, summary
                    except:
                        pass
    except Exception as e:
        print(f"Hugging Face error: {str(e)}")
    
    # Fallback to basic TF-IDF scoring
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        return score, "Basic resume analysis completed."
    except:
        return 0, "Unable to analyze resume."

async def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """Extract text from PDF file"""
    try:
        content = await pdf_file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        return ""

@router.post("/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can upload resumes"
        )
    
    # Extract text from PDF
    resume_text = await extract_text_from_pdf(resume)
    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from PDF"
        )
    
    # Save resume text to database
    await db.candidates.update_one(
        {"user_id": current_user.id},
        {
            "$set": {
                "resume_text": resume_text,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return {"message": "Resume uploaded successfully"}

@router.post("/apply/{job_id}")
async def apply_for_job(
    job_id: str,
    cover_letter: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply for jobs"
        )
    
    # Check if job exists
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    existing_application = await db.applications.find_one({
        "job_id": job_id,
        "candidate_id": current_user.id
    })
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied for this job"
        )
    
    # Get candidate's resume
    candidate = await db.candidates.find_one({"user_id": current_user.id})
    if not candidate or "resume_text" not in candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload your resume first"
        )
    
    # Analyze resume with AI
    score, summary = await analyze_resume_with_ai(
        candidate["resume_text"],
        job["description"]
    )
    
    # Create application
    application = JobApplication(
        job_id=job_id,
        candidate_id=current_user.id,
        resume_url="",  # TODO: Implement file storage
        cover_letter=cover_letter,
        ai_score=score,
        ai_summary=summary
    )
    
    result = await db.applications.insert_one(application.dict())
    
    # Update job application count
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$inc": {"total_applications": 1}}
    )
    
    return {"message": "Application submitted successfully", "application_id": str(result.inserted_id)}

@router.get("/applications")
async def get_applications(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view their applications"
        )
    
    cursor = db.applications.find({"candidate_id": current_user.id})
    applications = await cursor.to_list(length=100)
    
    # Get job details for each application
    for app in applications:
        job = await db.jobs.find_one({"_id": ObjectId(app["job_id"])})
        if job:
            app["job"] = job
    
    return applications

@router.get("/applications/{application_id}")
async def get_application(
    application_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    application = await db.applications.find_one({"_id": ObjectId(application_id)})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CANDIDATE and application["candidate_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get job details
    job = await db.jobs.find_one({"_id": ObjectId(application["job_id"])})
    if job:
        application["job"] = job
    
    return application 