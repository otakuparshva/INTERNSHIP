from fastapi import APIRouter, Depends, HTTPException, status, Query
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

async def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    try:
        yield db
    finally:
        client.close()

@router.get("/")
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    job_type: Optional[str] = None,
    db: AsyncIOMotorClient = Depends(get_db)
):
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if job_type:
        query["type"] = job_type
    
    # Get total count
    total = await db.jobs.count_documents(query)
    
    # Get jobs
    cursor = db.jobs.find(query).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for job in jobs:
        job["_id"] = str(job["_id"])
    
    return {
        "total": total,
        "jobs": jobs
    }

@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncIOMotorClient = Depends(get_db)):
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        job["_id"] = str(job["_id"])
        return job
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID"
        )

@router.post("/")
async def create_job(
    job: dict,
    db: AsyncIOMotorClient = Depends(get_db)
):
    job["created_at"] = datetime.utcnow()
    result = await db.jobs.insert_one(job)
    job["_id"] = str(result.inserted_id)
    return job

@router.put("/{job_id}")
async def update_job(
    job_id: str,
    job_update: dict,
    db: AsyncIOMotorClient = Depends(get_db)
):
    try:
        result = await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": job_update}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return {"message": "Job updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID"
        )

@router.delete("/{job_id}")
async def delete_job(job_id: str, db: AsyncIOMotorClient = Depends(get_db)):
    try:
        result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return {"message": "Job deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID"
        ) 