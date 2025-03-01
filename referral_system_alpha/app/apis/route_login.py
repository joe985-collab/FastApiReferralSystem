from datetime import timedelta

from apis.utils import OAuth2PwdBearer


# from core.config import settings
from utils import MyHasher
# from core.security import create_access_token
from apis.get_user_login import get_user
from database import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from schemas import Token
from sqlalchemy.orm import Session
from apis.security import create_access_token

router = APIRouter()

def authenticate_user(username:str,password:str,db:Session = Depends(get_db)):

    user = get_user(username=username,db=db)

    if not user:
        return False
    
    if not MyHasher.verify_password(password,user.password):
        return False
    
    return user

@router.post("/token",response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username,form_data.password,db)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data = {"sub":user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token":access_token,"token_type":"bearer"}

oauth2_scheme =  OAuth2PwdBearer(tokenUrl="/login/token")