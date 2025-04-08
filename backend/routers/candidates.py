from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
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
import logging
from routers.auth import get_current_user

from models.job import JobApplication
from models.user import UserResponse, UserRole

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

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

async def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    try:
        yield db
    finally:
        client.close()

@router.get("/profile")
async def get_candidate_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Get the candidate's profile"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access candidate profile"
        )
    
    try:
        candidate = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        # Remove sensitive information
        candidate["_id"] = str(candidate["_id"])
        if "hashed_password" in candidate:
            del candidate["hashed_password"]
        
        return candidate
    except Exception as e:
        logger.error(f"Error getting candidate profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the profile"
        )

@router.put("/profile")
async def update_candidate_profile(
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Update the candidate's profile"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update candidate profile"
        )
    
    try:
        update_data = {}
        if full_name:
            update_data["full_name"] = full_name
        if email:
            # Check if email is already taken
            existing_user = await db.users.find_one({"email": email, "_id": {"$ne": ObjectId(current_user["id"])}})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            update_data["email"] = email
        if phone:
            update_data["phone"] = phone
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        return {"message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating candidate profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile"
        )

@router.post("/resume")
async def update_resume(
    resume: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Update the candidate's resume"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update resume"
        )
    
    try:
        # Save resume file
        resume_path = f"uploads/resumes/{current_user['id']}_{resume.filename}"
        os.makedirs("uploads/resumes", exist_ok=True)
        
        with open(resume_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
        
        # Update user record
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {"resume_path": resume_path, "resume_updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        return {"message": "Resume updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the resume"
        )

@router.post("/apply/{job_id}")
async def apply_for_job(
    job_id: str,
    cover_letter: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Apply for a job"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply for jobs"
        )
    
    try:
        # Check if job exists
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if already applied
        existing_application = await db.applications.find_one({
            "job_id": ObjectId(job_id),
            "candidate_id": ObjectId(current_user["id"])
        })
        
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied for this job"
            )
        
        # Get candidate's resume
        candidate = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        if not candidate or "resume_path" not in candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please upload a resume before applying"
            )
        
        # Create application
        application = {
            "job_id": ObjectId(job_id),
            "candidate_id": ObjectId(current_user["id"]),
            "recruiter_id": job.get("recruiter_id"),
            "cover_letter": cover_letter,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.applications.insert_one(application)
        application["_id"] = str(result.inserted_id)
        
        # Log the application
        await db.activity_logs.insert_one({
            "type": "job_application",
            "user_id": ObjectId(current_user["id"]),
            "job_id": ObjectId(job_id),
            "details": {"status": "pending"},
            "timestamp": datetime.utcnow()
        })
        
        return {"message": "Application submitted successfully", "application_id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying for job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting the application"
        )

@router.get("/applications")
async def get_candidate_applications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Get all applications for the candidate"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications"
        )
    
    try:
        # Get applications with job details
        pipeline = [
            {"$match": {"candidate_id": ObjectId(current_user["id"])}},
            {"$sort": {"created_at": -1}},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": "$job"},
            {
                "$project": {
                    "_id": 1,
                    "job_id": 1,
                    "status": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "job.title": 1,
                    "job.company": 1,
                    "job.location": 1,
                    "job.type": 1
                }
            }
        ]
        
        applications = await db.applications.aggregate(pipeline).to_list(length=100)
        
        # Convert ObjectId to string
        for app in applications:
            app["_id"] = str(app["_id"])
            app["job_id"] = str(app["job_id"])
        
        return applications
    except Exception as e:
        logger.error(f"Error getting applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving applications"
        )

@router.get("/interviews")
async def get_candidate_interviews(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db)
):
    """Get all interviews for the candidate"""
    if current_user["role"] != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view interviews"
        )
    
    try:
        # Get interviews with job details
        pipeline = [
            {"$match": {"candidate_id": ObjectId(current_user["id"])}},
            {"$sort": {"created_at": -1}},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {"$unwind": "$job"},
            {
                "$project": {
                    "_id": 1,
                    "job_id": 1,
                    "status": 1,
                    "score": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "job.title": 1,
                    "job.company": 1
                }
            }
        ]
        
        interviews = await db.interviews.aggregate(pipeline).to_list(length=100)
        
        # Convert ObjectId to string
        for interview in interviews:
            interview["_id"] = str(interview["_id"])
            interview["job_id"] = str(interview["job_id"])
        
        return interviews
    except Exception as e:
        logger.error(f"Error getting interviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving interviews"
        ) 