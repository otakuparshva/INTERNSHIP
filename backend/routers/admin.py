from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pydantic import BaseModel
from pathlib import Path
import shutil
from ..core.auth import get_current_admin_user
from ..core.config import settings
from ..models.admin import ErrorLog, BackupLog
from ..core.logging import setup_logger

from models.user import UserResponse, UserRole
from routers.auth import get_database

load_dotenv()

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

class ErrorLog(BaseModel):
    timestamp: datetime
    level: str
    message: str
    details: Optional[str] = None

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: UserResponse = Depends(get_current_admin_user),
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
    current_user: UserResponse = Depends(get_current_admin_user),
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

@router.get("/error-logs")
async def get_error_logs(
    current_user: UserResponse = Depends(get_current_admin_user),
    severity: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    try:
        # Read logs from file
        log_file = Path("app.log")
        logs = []
        
        if log_file.exists():
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        log_data = json.loads(line)
                        # Apply filters
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
    current_user = Depends(get_current_admin_user),
    logs: List[ErrorLog]
):
    try:
        # Create export directory if it doesn't exist
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        # Generate export file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"error_logs_{timestamp}.csv"
        
        with open(export_file, "w") as f:
            # Write CSV header
            f.write("Timestamp,Severity,Source,Message,IP Address\n")
            
            # Write log entries
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
async def create_backup(current_user = Depends(get_current_admin_user)):
    try:
        # Create backup directory if it doesn't exist
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        # Collect data to backup
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "users": await get_users_data(),
            "jobs": await get_jobs_data(),
            "applications": await get_applications_data(),
            "settings": await get_settings_data()
        }
        
        # Write backup file
        with open(backup_file, "w") as f:
            json.dump(backup_data, f, indent=2)
        
        # Create backup log entry
        backup_log = BackupLog(
            id=str(backup_file),
            timestamp=datetime.now(),
            size=backup_file.stat().st_size,
            status="completed"
        )
        
        return backup_log
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create backup")

@router.post("/restore")
async def restore_backup(
    current_user = Depends(get_current_admin_user),
    backup: UploadFile = File(...)
):
    try:
        # Validate backup file
        if not backup.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Invalid backup file format")
        
        # Read backup data
        backup_data = json.loads(await backup.read())
        
        # Validate backup data structure
        required_keys = ["timestamp", "users", "jobs", "applications", "settings"]
        if not all(key in backup_data for key in required_keys):
            raise HTTPException(status_code=400, detail="Invalid backup data structure")
        
        # Restore data
        await restore_users_data(backup_data["users"])
        await restore_jobs_data(backup_data["jobs"])
        await restore_applications_data(backup_data["applications"])
        await restore_settings_data(backup_data["settings"])
        
        return {"message": "Backup restored successfully"}
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to restore backup")

@router.get("/backup/{backup_id}/download")
async def download_backup(
    backup_id: str,
    current_user = Depends(get_current_admin_user)
):
    try:
        backup_file = Path("backups") / f"{backup_id}.json"
        
        if not backup_file.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        return FileResponse(
            backup_file,
            media_type="application/json",
            filename=backup_file.name
        )
    except Exception as e:
        logger.error(f"Error downloading backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download backup")

# Helper functions for backup/restore
async def get_users_data():
    # Implement user data collection
    pass

async def get_jobs_data():
    # Implement job data collection
    pass

async def get_applications_data():
    # Implement application data collection
    pass

async def get_settings_data():
    # Implement settings data collection
    pass

async def restore_users_data(users_data):
    # Implement user data restoration
    pass

async def restore_jobs_data(jobs_data):
    # Implement job data restoration
    pass

async def restore_applications_data(applications_data):
    # Implement application data restoration
    pass

async def restore_settings_data(settings_data):
    # Implement settings data restoration
    pass

@router.post("/maintenance")
async def trigger_maintenance(
    action: str,
    current_user: UserResponse = Depends(get_current_admin_user),
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