from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from models.user import (
    UserCreate, UserLogin, UserResponse, Token, TokenData,
    PasswordReset, PasswordUpdate, UserRole
)
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database dependency
async def get_database():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    try:
        yield db
    finally:
        client.close()

# Security functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    return UserResponse(**user)

# Role-based access control
async def get_current_admin(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_recruiter(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Routes
@router.post("/register")
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    resume: Optional[UploadFile] = File(None),
    db: AsyncIOMotorClient = Depends(get_database)
):
    # Check if user already exists
    if await db.users.find_one({"email": email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user object
    user = {
        "full_name": full_name,
        "email": email,
        "hashed_password": pwd_context.hash(password),
        "role": "candidate",
        "created_at": datetime.utcnow()
    }
    
    # Save resume file if provided
    if resume:
        resume_path = f"uploads/resumes/{email}_{resume.filename}"
        os.makedirs("uploads/resumes", exist_ok=True)
        with open(resume_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
        user["resume_path"] = resume_path
    
    result = await db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

# Define a model for JSON login requests
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(),
    json_data: Optional[LoginRequest] = None,
    db: AsyncIOMotorClient = Depends(get_database)
):
    # Get email from either form data or JSON
    email = form_data.username if form_data else json_data.username
    password = form_data.password if form_data else json_data.password
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    user = await db.users.find_one({"email": email})
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

@router.post("/logout")
async def logout():
    # In a stateless JWT setup, the client handles logout by removing the token
    return {"message": "Successfully logged out"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    user = await db.users.find_one({"email": reset_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate reset token
    reset_token = create_access_token(
        data={"sub": user["email"], "type": "reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # TODO: Send reset email with token
    return {"message": "Password reset email sent"}

@router.put("/update-password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    user = await db.users.find_one({"_id": ObjectId(current_user.id)})
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": get_password_hash(password_data.new_password)}}
    )
    
    return {"message": "Password updated successfully"} 