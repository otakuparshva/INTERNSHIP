from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import json
import logging
from pydantic import BaseModel
from pathlib import Path
import shutil

from auth import get_current_admin_user
from core.config import settings
from models.admin import ErrorLog, BackupLog
from core.logging import setup_logger
from models.user import UserResponse, UserRole
from routers.auth import get_database

router = APIRouter(prefix="/admin", tags=["admin"])
logger = setup_logger(__name__)

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv("LOG_FILE", "app.log")
)

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

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncIOMotorClient = Depends(get_database), # type: ignore
    current_user: UserResponse = Depends(get_current_admin_user)
):
    total_users = await db.users.count_documents({})
    total_jobs = await db.jobs.count_documents({})
    total_applications = await db.applications.count_documents({})
    total_interviews = await db.interviews.count_documents({})

    active_recruiters = await db.users.count_documents({
        "role": UserRole.RECRUITER,
        "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })
    active_candidates = await db.users.count_documents({
        "role": UserRole.CANDIDATE,
        "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
    })

    jobs_by_status = {}
    for status in ["open", "closed", "draft"]:
        count = await db.jobs.count_documents({"status": status})
        jobs_by_status[status] = count

    applications_by_status = {}
    for status in ["pending", "reviewed", "accepted", "rejected", "interview_scheduled"]:
        count = await db.applications.count_documents({"status": status})
        applications_by_status[status] = count

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
    db: AsyncIOMotorClient = Depends(get_database), # type: ignore
    current_user: UserResponse = Depends(get_current_admin_user)
):
    query = {}
    if role:
        query["role"] = role

    cursor = db.users.find(query)
    users = await cursor.to_list(length=100)

    for user in users:
        user.pop("hashed_password", None)

    return users

@router.get("/error-logs")
async def get_error_logs(
    severity: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    try:
        log_file = Path("app.log")
        logs = []

        if log_file.exists():
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        log_data = json.loads(line)
                        if severity and log_data.get("severity") != severity:
                            continue
                        if source and log_data.get("source") != source:
                            continue
                        if start_date and datetime.fromisoformat(log_data["timestamp"]) < start_date:
                            continue
                        if end_date and datetime.fromisoformat(log_data["timestamp"]) > end_date:
                            continue
                        logs.append(log_data)
                    except json.JSONDecodeError:
                        continue

        return logs
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch error logs")

@router.post("/export-logs")
async def export_logs(
    logs: List[ErrorLog],
    current_user: UserResponse = Depends(get_current_admin_user)
):
    try:
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"error_logs_{timestamp}.csv"

        with open(export_file, "w") as f:
            f.write("Timestamp,Severity,Source,Message,IP Address\n")
            for log in logs:
                f.write(f"{log.timestamp},{log.severity},{log.source},{log.message},{log.ip_address}\n")

        return FileResponse(
            export_file,
            media_type="text/csv",
            filename=f"error_logs_{timestamp}.csv"
        )
    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export logs")

@router.post("/backup")
async def create_backup(
    db: AsyncIOMotorClient = Depends(get_database), # type: ignore
    current_user: UserResponse = Depends(get_current_admin_user)
):
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Logic for creating the backup file will go here

        return {"message": "Backup created successfully."}
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create backup")