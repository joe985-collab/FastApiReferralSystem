from apis.route_login import login_for_access_token, get_current_user
from database import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request,Response
from fastapi import status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth.forms import LoginForm
from fastapi.responses import RedirectResponse
from schemas import User


templates = Jinja2Templates(directory="templates")
router = APIRouter()




@router.get("/login")
def login(request: Request,msg:str = "default"):

    if msg=="noauth":
        response =  templates.TemplateResponse("auth/login.html",{"request": request,"errors":["Not Authenticated!"]})
        return response
    messages = {"reset_password":"Password reset successfully!","default":""}
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
    print("error")
    return templates.TemplateResponse("auth/login.html",form.__dict__)

@router.get("/dashboard")
async def dashboard(request: Request,current_user: User = Depends(get_current_user)):
    try:
        if not current_user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="noauth",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        response =  templates.TemplateResponse("components/dashboard.html",{"request": request,"user": current_user})
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except HTTPException as e:
            # return {"error":f"{e.detail}"}
            return RedirectResponse(url="/login?msg=noauth",status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(response: Response,current_user:User=Depends(get_current_user)):
    response = RedirectResponse(url="/login",status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response
