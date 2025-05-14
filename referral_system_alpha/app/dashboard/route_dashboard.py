from apis.route_login import get_current_user,get_current_user_id, get_current_ref_code,get_current_user_points,get_current_image_path
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
from datetime import datetime
from sqlalchemy.orm import Session
from models import User,ImageMetadata,Transactions,PointsLedger,TempVideo
from schemas import Points,Transaction
from database import get_db
from decimal import Decimal
import os
# Learn about webauthn library, fido and passkeys
os.chdir(os.getcwd())
templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.post("/upload_image")
def uploadImage(request:Request,file:UploadFile = File(...),current_user: User=Depends(get_current_user),db=Depends(get_db),ref_code:str = Depends(get_current_ref_code), points:int = Depends(get_current_user_points) ):

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
            user = db.query(User).filter(User.username == current_user.username).first()
            file_name = file.filename
            file_path = f"static/images/{file.filename}"
            file_size_kb = os.stat(f"static/images/{file.filename}").st_size/1024
            new_image = db.query(ImageMetadata).filter(ImageMetadata.user_id == str(user.id)).first()
            print("New_image",new_image.file_path)
            new_image.file_name = file_name
            new_image.file_path = file_path
            new_image.file_size_kb = file_size_kb
            db.commit()
            db.refresh(new_image)
            db.close()
        except Exception as e:
             raise HTTPException(status_code=500, detail=f'Something went wrong {e}')
        finally:
             file.file.close()
        # return {"message": f"Successfully uploaded {file.filename}"} 
        response =  templates.TemplateResponse("components/dashboard.html",{"request": request,"user": current_user,"default_image":f"images/{file.filename}","referral_code":ref_code,"points":points, "today":datetime.today().strftime('%Y-%m-%d')})
        return response
    except HTTPException as e:
            if e.detail == "noauth":
                return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)

            else:
                 return {"error":f"{e.detail}"}

@router.post("/confirm-transaction")
async def confirm_transaction(request:Request,current_user: User = Depends(get_current_user_id),db=Depends(get_db)):
     
     try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="noauth",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        form = await request.form()
        purchased = form.get("cost_tag")
        transaction = Transaction(user_id=current_user.id,amount=Decimal(purchased),status="pending")
        new_transaction = Transactions(**transaction.model_dump())
        db.add(new_transaction)
        new_transaction.status = "completed"
        db.commit()
        db.close()
        response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
        return response
     
     except HTTPException as e:
            if e.detail == "noauth":
                return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)

            else:
                 return {"error":f"{e.detail}"}

@router.get("/dashboard/video-upload")
async def uploaded_video(request:Request ,current_user: User = Depends(get_current_user)):
        if not current_user:
             return None
        return templates.TemplateResponse("components/video_route.html",{"request":request,"user":current_user})

@router.get("/dashboard/videos")
async def get_videos(request:Request ,current_user: User = Depends(get_current_user_id),db:Session = Depends(get_db)):
        if not current_user:
             return None
        video = db.query(TempVideo).filter(TempVideo.user_id == current_user.id).first()
        if not video:
            return RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("components/analyze_video.html",{"request":request,"user":current_user,"default_video":f"videos/{video.filename}"})
        
@router.post("/video-upload")
def uploaded_video(video_file: UploadFile = File(...),current_user: User = Depends(get_current_user),db:Session = Depends(get_db)):
     if not current_user:
          return None
     contents = video_file.file.read()

     file_path = f"static/videos/{video_file.filename}"

     with open(file_path,"wb") as f:
          f.write(contents)

     user = db.query(User).filter(User.username == current_user.username).first()
     filename = video_file.filename
     file_size_kb = os.stat(file_path).st_size/1024

     new_video = db.query(TempVideo).filter(TempVideo.user_id == user.id).first()
     if not new_video:
            new_video = TempVideo(user_id=user.id,filename=filename,file_path=file_path,file_size_kb=file_size_kb)
            db.add(new_video)
     else:  
            new_video.filename = filename
            new_video.file_path = file_path
            new_video.file_size_kb = file_size_kb
     db.commit()
     db.refresh(new_video)
     db.close()
     video_file.file.close()
     return RedirectResponse(url="/dashboard/videos",status_code=status.HTTP_303_SEE_OTHER)
