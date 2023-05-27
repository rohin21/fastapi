from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
import models
from schema import UserResponse, CreateUser
from db import get_db
from utils import hash

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_post(user: CreateUser, db: Session = Depends(get_db)):
    user.password = hash(user.password)
    new_user = models.Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    if new_user is None:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="User not created")
    return new_user


@router.get("/{id}", status_code=status.HTTP_302_FOUND, response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user with id {id}")
    return user
