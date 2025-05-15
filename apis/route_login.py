from datetime import timedelta,timezone,datetime

from apis.utils import OAuth2PwdBearer


# from core.config import settings
from utils import MyHasher
# from core.security import create_access_token
from apis.get_user_login import get_user,get_image_path,get_ref_code,get_user_points,get_user_id
from database import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from schemas import Token, User
from sqlalchemy.orm import Session
from apis.security import create_access_token,decode_token
from auth.TwoFA_Session import TempUserData
from datetime import datetime

router = APIRouter()
oauth2_scheme =  OAuth2PwdBearer(tokenUrl="/token")

def authenticate_user(email:str,password:str,db:Session = Depends(get_db)):

    user = get_user(email=email,db=db)

    if not user:
        return False
    if not MyHasher.verify_password(password,user.password):
        return False
    
    return user


def get_current_user(token: str = Depends(oauth2_scheme),db:Session = Depends(get_db)):
    
<<<<<<< HEAD
    print("Hereeeeeeeeeeee")
    if token:
        id = decode_token(token)
        print("ID",id)
=======
    if token:
        id = decode_token(token)
>>>>>>> fdfa1b0c8b410a16906486f74f7b1088fa46a2ea
        user = get_user_id(id=id,db=db)
        if user:
            return User(username=user.username)
    #     raise HTTPException(
    #         status_code = status.HTTP_401_UNAUTHORIZED,
    #         detail = "Invalid authentication credentials",
    #         headers = {"WWW-Authenticate":"Bearer"}
    #     )
def get_current_user_id(token: str = Depends(oauth2_scheme),db:Session = Depends(get_db)):
    
    if token:
        id = decode_token(token)
        user = get_user_id(id=id,db=db)
        if user:
            return user
        
def get_current_image_path(token: str = Depends(oauth2_scheme),db:Session = Depends(get_db)):
       
    if token:    
        id = decode_token(token)
        user = get_user_id(id=id,db=db)
        if user:
             return get_image_path(user_id=user.id,db=db)

        
def get_current_ref_code(token: str = Depends(oauth2_scheme),db:Session = Depends(get_db)):
       
    if token:
        id = decode_token(token)
        user = get_user_id(id=id,db=db)
        if user:
            return get_ref_code(user_id=user.id,db=db)
      
    
def get_current_user_points(token:str = Depends(oauth2_scheme),db:Session = Depends(get_db)):

    if token:
        id = decode_token(token)
        user = get_user_id(id=id,db=db)
        if user:
            return get_user_points(user_id=user.id,db=db)
    

@router.post("/token",response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.email,form_data.password,db)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = datetime.now(timezone.utc)+timedelta(minutes=30)
    refresh_token_expires = datetime.now(timezone.utc)+timedelta(days=7)
   
    access_token = create_access_token(
        data = {"sub":str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data = {"sub":str(user.id)}, expires_delta=refresh_token_expires
    )
    response.set_cookie(                    
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    response.set_cookie(
        key="refresh_token", value=f"Bearer {refresh_token}", httponly=True
    )       
  
    return {"access_token":access_token, "refresh_token":refresh_token,"token_type":"bearer"}

@router.post("/token",response_model=Token)
def login_for_access_token_register(
    response: Response,
    session_data: TempUserData,
    db: Session = Depends(get_db),
):
    user = authenticate_user(session_data.email,session_data.password_plain,db)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    

    access_token_expires = datetime.now(timezone.utc)+timedelta(minutes=30)
    refresh_token_expires = datetime.now(timezone.utc)+timedelta(days=7)
    access_token = create_access_token(
        data = {"sub":user.id}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data = {"sub":user.id}, expires_delta=refresh_token_expires
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    response.set_cookie(
        key="refresh_token", value=f"Bearer {refresh_token}", httponly=True
    )
    return {"access_token":access_token, "refresh_token":refresh_token,"token_type":"bearer"}