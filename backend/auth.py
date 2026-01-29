from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from dependencies import db_dependency
from models import Users

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "170c975e9b0c80e6e21725ed9793b70e7cdbf9f168bad4a13056d865568a16af"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


MAX_BCRYPT_LENGTH = 72

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    password_to_hash = create_user_request.password[:MAX_BCRYPT_LENGTH]  # truncate if needed
    user = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(password_to_hash),
    )
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}



def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload.get("sub"), "id": payload.get("id")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        user.username, user.id, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}
