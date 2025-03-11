from fastapi import FastAPI, Depends, HTTPException, status, APIRouter,Request,Form
from starlette.responses import JSONResponse,HTMLResponse
from database import get_db
from apis.get_user_login import get_user
from starlette.background import BackgroundTasks
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, MessageType,ConnectionConfig
from jose import jwt, JWTError
from schemas import ForgetPasswordRequest,ResetForgetPassword,SuccessMessage,EmailTemplateSchema
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from utils import MyHasher
import os
import json

load_dotenv(os.path.join('apis', '.env'))

FORGET_PWD_SECRET_KEY = str(os.getenv("FORGET_PWD_SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))

router = APIRouter()

templates = Jinja2Templates(directory="templates")

def create_reset_password_token(email:str):
    data = {"sub": email, "exp": datetime.now(timezone.utc)+timedelta(minutes=10)}
    token = jwt.encode(data, FORGET_PWD_SECRET_KEY,ALGORITHM)
    return token


conf = ConnectionConfig(
    MAIL_USERNAME="bharalijyotirmoy@gmail.com",
    MAIL_PASSWORD="*************",
    MAIL_FROM="bharalijyotirmoy@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = "templates"
)


def decode_reset_password_token(token: str):
    try:
        payload = jwt.decode(token,FORGET_PWD_SECRET_KEY,ALGORITHM)
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None

def get_form_data(
    new_password: str = Form(...),
    confirm_password: str = Form(...)
    ):
    return ResetForgetPassword(new_password=new_password,confirm_password=confirm_password)

@router.get("/forget-password")
async def forget_password(request: Request):
    return templates.TemplateResponse("components/forget_password.html",{"request":request})


@router.post("/forget-password")
async def forget_password(
    background_tasks: BackgroundTasks,
    eml: ForgetPasswordRequest = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = get_user(username=eml.email,db=db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Invalid Email Address")

        secret_token = create_reset_password_token(email=eml.email)
        forget_url_link = f"http://localhost:8000/reset-password/{secret_token}"

        email_body = {"username":user.username,"link_expiry_min":"30","reset_link":forget_url_link}
        # template_data = EmailTemplateSchema.model_validate(email_body)
        # print(template_data)

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[eml.email],
            template_body=email_body,
            subtype="html"
        )

        template_name = "components/password_reset.html"
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message,message,template_name)

        return JSONResponse(status_code=status.HTTP_200_OK,
            content = {"message":"Email has been sent","success":True,
            "status_code": status.HTTP_200_OK
            } 
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail = f"Something Unexpected, Server Error {e}"
        )

@router.get("/reset-password/{reset_token}",response_class=HTMLResponse)
async def reset_password_page(request: Request, reset_token: str):
    
    try:
        info = decode_reset_password_token(token=reset_token)
        # reset_token = rfp.secret_token
        
        if info is None:
            raise HTTPException(status_code=400,detail="Invalid or expired reset token")

        return templates.TemplateResponse("components/reset_password_page.html",{"request":request,"reset_token":reset_token})
    
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Some thing unexpected happened! {e}")


@router.post("/reset-password/{reset_token}",response_model=SuccessMessage)
async def reset_password(reset_token: str,rfp: ResetForgetPassword = Depends(get_form_data), db: Session = Depends(get_db)):

    try:
        
        info  = decode_reset_password_token(token=reset_token)

        if info is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="New password and confirm password are not same.")
        
        if rfp.new_password != rfp.confirm_password:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="New password and confirm password are not same.")

        hashed_password = MyHasher.hash_password(rfp.new_password)
        # print(info)
        user = get_user(username=info,db=db)
        user.password = hashed_password
        db.commit()
        db.refresh(user)
        return {'success':True, 'status_code':status.HTTP_200_OK,'message':'Password Reset Successful!'}

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Some thing unexpected happened: {e}")

