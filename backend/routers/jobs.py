from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv
import aiohttp
import json

from models.job import (
    JobCreate, JobUpdate, JobResponse, JobSearch,
    JobStatus, JobInDB
)
from models.user import UserResponse, UserRole
from routers.auth import get_current_user, get_current_recruiter, get_database

load_dotenv()

router = APIRouter()

# AI Service configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

async def generate_jd_with_ai(title: str, requirements: List[str]) -> str:
    """Generate job description using AI (Hugging Face or Ollama)"""
    try:
        # Try Ollama first
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"Generate a professional job description for the role of {title}. Requirements: {', '.join(requirements)}",
                    "stream": False
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
    except Exception as e:
        print(f"Ollama error: {str(e)}")
    
    # Fallback to Hugging Face
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={
                    "inputs": f"Generate a professional job description for the role of {title}. Requirements: {', '.join(requirements)}",
                    "parameters": {
                        "max_length": 500,
                        "temperature": 0.7
                    }
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result[0].get("generated_text", "")
    except Exception as e:
        print(f"Hugging Face error: {str(e)}")
    
    return ""

@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    # Generate AI description
    ai_description = await generate_jd_with_ai(job.title, job.requirements)
    
    # Create job document
    job_dict = job.dict()
    job_dict["recruiter_id"] = current_user.id
    job_dict["created_at"] = datetime.utcnow()
    job_dict["updated_at"] = datetime.utcnow()
    job_dict["ai_generated_description"] = ai_description
    
    result = await db.jobs.insert_one(job_dict)
    job_dict["_id"] = result.inserted_id
    
    return JobResponse(**job_dict)

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    search: Optional[JobSearch] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {}
    
    if search:
        if search.query:
            query["$or"] = [
                {"title": {"$regex": search.query, "$options": "i"}},
                {"description": {"$regex": search.query, "$options": "i"}}
            ]
        if search.status:
            query["status"] = search.status
        if search.recruiter_id:
            query["recruiter_id"] = search.recruiter_id
    
    # If user is a candidate, only show open jobs
    if current_user.role == UserRole.CANDIDATE:
        query["status"] = JobStatus.OPEN
    
    # If user is a recruiter, only show their jobs
    if current_user.role == UserRole.RECRUITER:
        query["recruiter_id"] = current_user.id
    
    skip = (search.page - 1) * search.limit if search else 0
    limit = search.limit if search else 10
    
    cursor = db.jobs.find(query).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    return [JobResponse(**job) for job in jobs]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.RECRUITER and job["recruiter_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return JobResponse(**job)

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job["recruiter_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update job
    update_data = job_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # If title or requirements changed, regenerate AI description
    if "title" in update_data or "requirements" in update_data:
        title = update_data.get("title", job["title"])
        requirements = update_data.get("requirements", job["requirements"])
        update_data["ai_generated_description"] = await generate_jd_with_ai(title, requirements)
    
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data}
    )
    
    updated_job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    return JobResponse(**updated_job)

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: UserResponse = Depends(get_current_recruiter),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user owns the job
    if job["recruiter_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    await db.jobs.delete_one({"_id": ObjectId(job_id)})
    return {"message": "Job deleted successfully"} 