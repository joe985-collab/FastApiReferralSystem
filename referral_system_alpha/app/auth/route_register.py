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
from apis.route_login import login_for_access_token
from fastapi import HTTPException
from apis.get_user_login import get_user
import secrets
from datetime import datetime,timedelta
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse,HTMLResponse
from schemas import UserCreate
from fastapi_mail import FastMail, MessageSchema, MessageType,ConnectionConfig
import os
from dotenv import load_dotenv
from random import randint
from auth.TwoFA_Session import backend,TempUserData,cookie,verifier
from uuid import UUID, uuid4


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
    return db.query(models.User).filter(models.User.username == name).first() or db.query(models.User).filter(models.User.email == email).first()

def check_item_by_referral_code_exists(db:Session, referral_code:str):
    return db.query(models.User).filter(models.User.referral_code == referral_code).first()

async def send_mail(
    eml: str,
    user: TempUserData,
    # db: Session = Depends(get_db),
):

    try:
        
        # background_tasks = BackgroundTasks()
    
        # activation_token = secrets.token_urlsafe(32)
        # expires_at = datetime.now(datetime.timezone.utc) + timedelta(minutes=30)
        
        otp = randint(0,1000)+randint(0,9000)
     
        # activate_link = f"http://localhost:8000/activate-link/{activation_token}"
        user.otp = otp
        email_body = {"username":user.username,"link_expiry_minutes":"30","activate_otp":otp}
        # template_data = EmailTemplateSchema.model_validate(email_body)
        # print(template_data)

        message = MessageSchema(
            subject="OTP Verification",
            recipients=[eml],
            template_body=email_body,
            subtype="html"
        )
        template_name = "components/verify_otp.html"
        fm = FastMail(conf)
        # background_tasks.add_task(fm.send_message,message,template_name)
        await fm.send_message(message,template_name)
        # print("status of mail",mail_status)
 

        return JSONResponse(status_code=status.HTTP_200_OK,
            content = {"message":"Email has been sent","success":True,
            "status_code": status.HTTP_200_OK
            } 
        )
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
#             response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
#             # login_for_access_token(form_data=form,db=db)
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
    form_datas = dict(await request.form())

    if await form.is_valid():

        try:
            session_id = uuid4()
            hashed_password = MyHasher.hash_password(form_datas.get("password"))
            new_user = TempUserData(username = form_datas.get("username"),email = form_datas.get("email"),password = hashed_password)        
            # await send_mail(eml=new_user.email,user=new_user) 
            # print("New user",new_user)   
            await backend.create(session_id, new_user)
            # stored_data = await backend.read(session_id)
            # print("Cookie Stat",stored_data)
            if check_item_by_name_exists(db,form_datas.get("username"),form_datas.get("email")):
                raise HTTPException(status_code=400,detail="Username or email already exists")
            if form_datas.get("referral_code"):
                if not check_item_by_referral_code_exists(db,form_datas.get("referral_code")):
                    raise HTTPException(status_code=400,detail="Referral code not found")
                new_user.referral_code = form_datas.get("referral_code")
            response = templates.TemplateResponse("components/otp_verification.html",{"request":request})
            cookie.attach_to_response(response, session_id)
            # form.__dict__.update(message="We’ve sent an activation link to your email address. Please activate your account within the next 7 days to verify your email and access all features.")
            # return templates.TemplateResponse("auth/register.html",{"message":""})
        except HTTPException as e:
            form.__dict__.get("errors").append(f"{e.detail}")
            return templates.TemplateResponse("auth/register.html",form.__dict__)
        
    return response

@router.get("/resend-otp")
async def resend_otp(request:Request,session_id:UUID = Depends(cookie),session_data: TempUserData = Depends(verifier)):
    if not session_data:
        raise HTTPException(status_code=403, detail="Invalid session")
        
    return {"test":True}

# def get_current_user(session_data: TempUserData = Depends(verifier)) -> TempUserData:
#     return session_data

@router.post("/verify-otp")
async def verify_password(request: Request,response:Response,session_id:UUID = Depends(cookie),session_data:TempUserData = Depends(verifier)):
    # session_data:TempUserData = Depends(verifier)
    try:
        # session_id = cookie(request)
        # session_data = await backend.read(session_id)
        # print(session_data.username)
        # print("request data: ",request.state.session_ids)
        if not session_data:
            raise HTTPException(status_code=403, detail="Invalid session")
        
        if datetime.now() >= session_data["expires_at"]:
             await backend.delete(session_id)
             cookie.delete_from_response(response)
             raise HTTPException(400, "Session expired")
        
        form_data = await request.form()
        return {"status": "success", "data": form_data}
        
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
