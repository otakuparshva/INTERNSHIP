from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ErrorLog(BaseModel):
    id: Optional[str] = None
    timestamp: datetime
    severity: str
    source: str
    message: str
    ip_address: Optional[str] = None
    user_id: Optional[str] = None
    stack_trace: Optional[str] = None

class BackupLog(BaseModel):
    id: str
    timestamp: datetime
    size: int
    status: str
    error: Optional[str] = None

class SystemStats(BaseModel):
    total_users: int
    total_jobs: int
    total_applications: int
    active_interviews: int
    system_uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    last_backup: Optional[datetime] = None
    error_count_24h: int
    api_requests_24h: int 