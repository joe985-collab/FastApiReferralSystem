from apis.route_login import login_for_access_token, get_current_user,get_current_image_path,oauth2_scheme
from database import get_db
from fastapi import APIRouter,Cookie
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request,Response
from fastapi import status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth.forms import LoginForm
from fastapi.responses import RedirectResponse
from schemas import User
from datetime import timedelta,timezone,datetime
from apis.security import create_access_token,get_exp_token
import models
from datetime import datetime
# Learn about webauthn library, fido and passkeys

templates = Jinja2Templates(directory="templates")
router = APIRouter()




@router.get("/login")
def login(request: Request,msg:str = "default",err:str=""):


    errors = {"noauth":"Not Authenticated!","invalid_session":"Invalid Session. Kindly register first."}
    messages = {"reset_password":"Password reset successfully!","default":""}

    if err:
        response =  templates.TemplateResponse("auth/login.html",{"request": request,"errors":[errors[err]]})
        return response
    if msg in messages:
        response =  templates.TemplateResponse("auth/login.html",{"request": request,"msg":messages[msg]})
        return response
    else:
        response =  templates.TemplateResponse("auth/login.html",{"request": request,"errors":["Invalid query"]})
        return response



@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):

    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():

        try:
            # form.__dict__.update(msg="Login Successful :")
            # response = templates.TemplateResponse("components/dashboard.html", form.__dict__)
            response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
            login_for_access_token(response=response,form_data=form,db=db)
            # login_for_access_token(form_data=form,db=db)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("auth/login.html",form.__dict__)
    return templates.TemplateResponse("auth/login.html",form.__dict__)


async def track_activity(user: User=Depends(get_current_user),db: Session = Depends(get_db)):

        if not user:
             return None
        
        # print(f"User is active at: {datetime.now()}")
        user_q = db.query(models.User).filter(models.User.username == user.username).first()
        user_q.last_active = datetime.now()
        db.commit()
        db.refresh(user_q)
        return "success"



def refresh_token(request:Request,refresh_token = Cookie(None, alias="refresh_token"),access_token:str=Depends(oauth2_scheme),db:Session = Depends(get_db),user:User=Depends(get_current_user),image_path:str = Depends(get_current_image_path)):
     if user:
        if refresh_token:
             my_user =  db.query(models.User).filter(models.User.username == user.username).first()
            #  user_last_active = my_user.last_active
             if (get_exp_token(access_token)-datetime.now()).total_seconds()//60 <= 2:
                    access_token_expires = datetime.now(timezone.utc)+timedelta(minutes=30)
                    refresh_token_expires = datetime.now(timezone.utc)+timedelta(days=7)
                    new_access_token = create_access_token(
                        data = {"sub":my_user.email}, expires_delta=access_token_expires
                    )
                    new_refresh_token = create_access_token(
                        data = {"sub":my_user.email}, expires_delta=refresh_token_expires
                    )
                    response =  templates.TemplateResponse("components/dashboard.html",{"request": request,"user": user,"default_image":f"images/{image_path}", "today":datetime.today().strftime('%Y-%m-%d')})
                    response.set_cookie(
                        key="access_token", value=f"Bearer {new_access_token}", httponly=True
                    )
                    response.set_cookie(
                        key="refresh_token", value=f"Bearer {new_refresh_token}", httponly=True
                    )
                    return response
       

@router.get("/dashboard")
async def dashboard(request: Request,current_user: User = Depends(get_current_user),image_path:str = Depends(get_current_image_path),_: str = Depends(track_activity),response:None = Depends(refresh_token)):
    try:
        if response:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        if not current_user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="noauth",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        response =  templates.TemplateResponse("components/dashboard.html",{"request": request,"user": current_user,"default_image":f"images/{image_path}", "today":datetime.today().strftime('%Y-%m-%d')})
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except HTTPException as e:
            # return {"error":f"{e.detail}"}
            return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(response: Response,current_user:User=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)
    response = RedirectResponse(url="/login",status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response
