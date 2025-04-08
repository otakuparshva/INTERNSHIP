from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pydantic import BaseModel

from models.user import UserResponse, UserRole
from routers.auth import get_current_admin, get_database

load_dotenv()

router = APIRouter()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv("LOG_FILE", "app.log")
)
logger = logging.getLogger(__name__)

class SystemStats(BaseModel):
    total_users: int
    total_jobs: int
    total_applications: int
    total_interviews: int
    active_recruiters: int
    active_candidates: int
    jobs_by_status: dict
    applications_by_status: dict
    interviews_by_status: dict

class ErrorLog(BaseModel):
    timestamp: datetime
    level: str
    message: str
    details: Optional[str] = None

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    # Get total counts
    total_users = await db.users.count_documents({})
    total_jobs = await db.jobs.count_documents({})
    total_applications = await db.applications.count_documents({})
    total_interviews = await db.interviews.count_documents({})
    
    # Get active users
    active_recruiters = await db.users.count_documents({
        "role": UserRole.RECRUITER,
        "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })
    active_candidates = await db.users.count_documents({
        "role": UserRole.CANDIDATE,
        "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })
    
    # Get jobs by status
    jobs_by_status = {}
    for status in ["open", "closed", "draft"]:
        count = await db.jobs.count_documents({"status": status})
        jobs_by_status[status] = count
    
    # Get applications by status
    applications_by_status = {}
    for status in ["pending", "reviewed", "accepted", "rejected", "interview_scheduled"]:
        count = await db.applications.count_documents({"status": status})
        applications_by_status[status] = count
    
    # Get interviews by status
    interviews_by_status = {}
    for status in ["pending", "in_progress", "completed", "cancelled"]:
        count = await db.interviews.count_documents({"status": status})
        interviews_by_status[status] = count
    
    return SystemStats(
        total_users=total_users,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_interviews=total_interviews,
        active_recruiters=active_recruiters,
        active_candidates=active_candidates,
        jobs_by_status=jobs_by_status,
        applications_by_status=applications_by_status,
        interviews_by_status=interviews_by_status
    )

@router.get("/users")
async def get_users(
    role: Optional[UserRole] = None,
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {}
    if role:
        query["role"] = role
    
    cursor = db.users.find(query)
    users = await cursor.to_list(length=100)
    
    # Remove sensitive information
    for user in users:
        user.pop("hashed_password", None)
    
    return users

@router.get("/logs/errors")
async def get_error_logs(
    level: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {}
    if level:
        query["level"] = level
    if start_date:
        query["timestamp"] = {"$gte": start_date}
    if end_date:
        query.setdefault("timestamp", {})["$lte"] = end_date
    
    cursor = db.error_logs.find(query).sort("timestamp", -1)
    logs = await cursor.to_list(length=100)
    return logs

@router.get("/logs/ai")
async def get_ai_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    query = {}
    if start_date:
        query["timestamp"] = {"$gte": start_date}
    if end_date:
        query.setdefault("timestamp", {})["$lte"] = end_date
    
    cursor = db.ai_logs.find(query).sort("timestamp", -1)
    logs = await cursor.to_list(length=100)
    return logs

@router.post("/backup")
async def trigger_backup(
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    try:
        # Create backup timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Get all collections
        collections = ["users", "jobs", "applications", "interviews", "candidates"]
        backup_data = {}
        
        for collection in collections:
            cursor = db[collection].find({})
            documents = await cursor.to_list(length=None)
            backup_data[collection] = documents
        
        # Save backup to file
        backup_file = f"backup_{timestamp}.json"
        with open(backup_file, "w") as f:
            json.dump(backup_data, f, default=str)
        
        # Log backup
        logger.info(f"Backup created successfully: {backup_file}")
        
        return {"message": "Backup created successfully", "file": backup_file}
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup failed"
        )

@router.post("/maintenance")
async def trigger_maintenance(
    action: str,
    current_user: UserResponse = Depends(get_current_admin),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    if action == "cleanup_old_logs":
        # Delete logs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        await db.error_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
        await db.ai_logs.delete_many({"timestamp": {"$lt": cutoff_date}})
        return {"message": "Old logs cleaned up successfully"}
    
    elif action == "archive_old_jobs":
        # Archive jobs older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        await db.jobs.update_many(
            {
                "created_at": {"$lt": cutoff_date},
                "status": "closed"
            },
            {"$set": {"archived": True}}
        )
        return {"message": "Old jobs archived successfully"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid maintenance action"
        ) 