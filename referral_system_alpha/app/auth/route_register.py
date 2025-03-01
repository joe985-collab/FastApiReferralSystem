import models
import schemas
from utils import MyHasher
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.post("/users/",response_model=schemas.UserResponse,status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        
        hashed_password = MyHasher.hash_password(user.password)
        # new_user = models.User(**user.model_dump())
        new_user = models.User(username=user.username,email=user.email,password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
