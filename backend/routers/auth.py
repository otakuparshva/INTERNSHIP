from fastapi import APIRouter, Depends, HTTPException, status
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

load_dotenv()

router = APIRouter()

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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
@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    # Check if user already exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    return UserResponse(**user_dict)

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorClient = Depends(get_database) # type: ignore
):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)

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