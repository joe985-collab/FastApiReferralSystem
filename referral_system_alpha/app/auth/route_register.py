import models
from utils import MyHasher
from fastapi import APIRouter,Response,Request
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from fastapi.templating import Jinja2Templates
from auth.forms import RegisterForm
from fastapi.responses import RedirectResponse
from fastapi import status
from apis.route_login import login_for_access_token_register
from fastapi import HTTPException
from apis.get_user_login import get_user
import secrets
from datetime import datetime,timedelta
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse,HTMLResponse
from fastapi_mail import FastMail, MessageSchema, MessageType,ConnectionConfig
import os
from dotenv import load_dotenv
from random import randint
from auth.TwoFA_Session import backend,TempUserData,cookie,verifier
from uuid import UUID, uuid4
from models import User


load_dotenv(os.path.join('apis', '.env'))

APP_PASSWORD = str(os.getenv("SMTP_PASSOWRD"))
templates = Jinja2Templates(directory="templates")
router = APIRouter()

conf = ConnectionConfig(
    MAIL_USERNAME="bharalijyotirmoy@gmail.com",
    MAIL_PASSWORD=APP_PASSWORD,
    MAIL_FROM="bharalijyotirmoy@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = "templates"
)

def check_item_by_name_exists(db:Session, name:str,email:str):
    return db.query(User).filter(User.username == name).first() or db.query(User).filter(User.email == email).first()

def check_item_by_referral_code_exists(db:Session, referral_code:str):
    return db.query(User).filter(User.referral_code == referral_code).first()

async def send_mail(
    eml: str,
    user: TempUserData,
    session_id: UUID
    # db: Session = Depends(get_db),
):

    try:
        
        # background_tasks = BackgroundTasks()
    
        # activation_token = secrets.token_urlsafe(32)
        # expires_at = datetime.now(datetime.timezone.utc) + timedelta(minutes=30)
        
        otp = randint(1000,9999)
     
        # activate_link = f"http://localhost:8000/activate-link/{activation_token}"
        user.otp = MyHasher.hash_password(str(otp))
        await backend.update(session_id,user)
        email_body = {"username":user.username,"link_expiry_minutes":"30","activate_otp":otp}

        message = MessageSchema(
            subject="OTP Verification",
            recipients=[eml],
            template_body=email_body,
            subtype="html"
        )
        template_name = "components/verify_otp.html"
        fm = FastMail(conf)
        await fm.send_message(message,template_name)
        # print("status of mail",mail_status)
 

        # return JSONResponse(status_code=status.HTTP_200_OK,
        #     content = {"message":"Email has been sent","success":True,
        #     "status_code": status.HTTP_200_OK
        #     } 
        # )
    except Exception as e:
        print("detail: ",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail = f"The email address you entered appears to be invalid or doesn't exist. Please check for typos and try again, or use a different email address.")

@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("auth/register.html",{"request":request})


# @router.get("/activate-link/{activation_token}",response_class=HTMLResponse)
# async def activation_page(request: Request, activation_token:str, db:Session = Depends(get_db)):
#         try:
#             # form.__dict__.update(msg="Login Successful :")
#             # response = templates.TemplateResponse("components/dashboard.html", form.__dict__)
#             user = db.query(models.User).filter(
#                     models.User.activation_token == activation_token,
#                     models.User.token_expires_at >= datetime.now(datetime.timezone.utc)
#                 ).first()
#               response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
                # login_for_access_token(form_data=form,db=db)
#             if not user:
#                 return templates.TemplateResponse("auth/login.html",{ "request": request, "msg": "Activation link has expired. Kindly verify through the dashboard."})
            
#             if not user.is_activated: 
#                 user.is_activated = True
#                 db.commit()
#                 db.refresh(user)
#                 db.close()
#                 print("token - datetime",user.token_expires_at.timestamp()//60 - datetime.utcnow().timestamp()//60)
#                 if user.token_expires_at.timestamp()//60 - datetime.utcnow().timestamp()//60 <= 30:
#                       return response
#                 else:
#                       return templates.TemplateResponse("components/activated_or_not.html",{ "request": request, "msg": "Your account has been activated :). I hope you enjoy the stay.","user":user})

#             else:
#                 return templates.TemplateResponse("components/activated_or_not.html",{ "request": request, "msg": "Your account is already activated.", "user":user})

          
        # except HTTPException as e:
        #     # form.__dict__.get("errors").append(f"{e.detail}")
        #     return templates.TemplateResponse("auth/register.html",form.__dict__)

@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):

    form = RegisterForm(request)
    await form.load_data()
    # form_datas = dict(await request.form())

    if await form.is_valid():

        try:
            session_id = uuid4()
            hashed_password = MyHasher.hash_password(form.password)
            new_user = TempUserData(username = form.username,email = form.email,password_plain=form.password,password = hashed_password,is_verified=False)        
            # print("New user",new_user)   
            await backend.create(session_id, new_user)

            await send_mail(eml=new_user.email,user=new_user,session_id=session_id) 
            # stored_data = await backend.read(session_id)
            # print("Cookie Stat",stored_data)
            if check_item_by_name_exists(db,form.username,form.email):
                raise HTTPException(status_code=400,detail="Username or email already exists")
            if form.referral_code:
                if not check_item_by_referral_code_exists(db,form.referral_code):
                    raise HTTPException(status_code=400,detail="Referral code not found")
                new_user.referral_code = form.referral_code
                new_user.referred_by = db.query(models.User.username).filter(
                    models.User.referral_code == form.referral_code
                ).first()
            response = templates.TemplateResponse("components/otp_verification.html",{"request":request,"register_form":form,"message":"An 4 digit OTP has been sent to your email. Kindly check and verify."})
            cookie.attach_to_response(response, session_id)
            return response
            # form.__dict__.update(message="We’ve sent an activation link to your email address. Please activate your account within the next 7 days to verify your email and access all features.")
            # return templates.TemplateResponse("auth/register.html",{"message":""})
        except HTTPException as e:
            form.__dict__.get("errors").append(f"{e.detail}")
            return templates.TemplateResponse("auth/register.html",form.__dict__)
        
    return response

@router.get("/resend-otp")
async def resend_otp(request:Request,response:Response,session_id:UUID = Depends(cookie),session_data: TempUserData = Depends(verifier)):
    if not session_data:
        raise HTTPException(status_code=403, detail="Invalid session") 
    
    if datetime.now() >= session_data.expires_at:
             await backend.delete(session_id)
             cookie.delete_from_response(response)
             raise HTTPException(400, "Session expired")
    await send_mail(eml=session_data.email,user=session_data,session_id=session_id)
    response =  templates.TemplateResponse("components/otp_verification.html",{"request":request,"message":"A 4 digit OTP has been resent to your email. Kindly check and verify."})
    return response
# def get_current_user(session_data: TempUserData = Depends(verifier)) -> TempUserData:
#     return session_data

@router.post("/verify-otp")
async def verify_password(request: Request,session_id:UUID = Depends(cookie),session_data:TempUserData = Depends(verifier),db=Depends(get_db)):
    # session_data:TempUserData = Depends(verifier)
    try:
        if not session_data:
            raise HTTPException(status_code=403, detail="Invalid session")
        if datetime.now() >= session_data.expires_at:
             await backend.delete(session_id)
             response = templates.TemplateResponse("auth/register.html")
             cookie.delete_from_response(response)
             raise HTTPException(400, "Session expired")
        
        form_data = await request.form()
        print("Session Data",session_data)
        if MyHasher.verify_password(form_data["totalOtp"],session_data.otp):
            session_data.is_verified = True
            # if session_data.referral_code:
            #     required_data = UserCreate(username=session_data.username,password=session_data.password,email=session_data.email,referral_code=session_data.referral_code,referred_by=session_data.referred_by)
            # else:
            #     required_data = UserCreate(username=session_data.username,password=session_data.password,email=session_data.email)
            db_user = User(**session_data.model_dump(exclude={"otp","expires_at","password_plain"}))
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            db.close()
            response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
            login_for_access_token_register(response=response,session_data=session_data,db=db)
            cookie.delete_from_response(response)
            return response
        return templates.TemplateResponse("components/otp_verification.html",{"request":request,"errors":["Invalid OTP. Please try again"]})
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# @router.post("/users/",response_model=schemas.UserResponse,status_code=201)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        
#         hashed_password = MyHasher.hash_password(user.password)
#         # new_user = models.User(**user.model_dump())
#         if check_item_by_name_exists(db,user.username,user.email):
#                 raise HTTPException(status_code=400,detail="Username or email already exists")
#         if not user.referral_code:
#                 new_user = models.User(username=user.username,email=user.email,password=hashed_password)
#         else:
#                 new_user = models.User(username=user.username,email=user.email,password=hashed_password,referral_code=user.referral_code)
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user
