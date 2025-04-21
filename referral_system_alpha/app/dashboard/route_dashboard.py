from apis.route_login import get_current_user
from database import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException,File,UploadFile
from fastapi import Request,Response
from fastapi import status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth.forms import LoginForm
from fastapi.responses import RedirectResponse
from schemas import User
from datetime import datetime
# Learn about webauthn library, fido and passkeys

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.post("/upload_image")
def uploadImage(request:Request,file:UploadFile = File(...),current_user: User=Depends(get_current_user)):

    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="noauth",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        try:
            contents = file.file.read()
            with open(f"static/images/{file.filename}","wb") as f:
                f.write(contents)
        except Exception as e:
             raise HTTPException(status_code=500, detail=f'Something went wrong {e}')
        finally:
             file.file.close()
        # return {"message": f"Successfully uploaded {file.filename}"} 
        response =  templates.TemplateResponse("components/dashboard.html",{"request": request,"user": current_user,"default_image":f"images/{file.filename}", "today":datetime.today().strftime('%Y-%m-%d')})
        return response
    except HTTPException as e:
            if e.detail == "noauth":
                return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)

            else:
                 return {"error":f"{e.detail}"}