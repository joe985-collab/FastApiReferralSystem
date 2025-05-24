from apis.route_login import get_current_user,get_current_user_id, get_current_ref_code,get_current_user_points,get_current_user_websocket
from database import get_db
from fastapi import APIRouter,Form
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException,File,UploadFile
from fastapi import Request,Response
from fastapi import status,WebSocket,WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth.forms import LoginForm
from fastapi.responses import RedirectResponse
from datetime import datetime
from sqlalchemy.orm import Session
from models import User,ImageMetadata,Transactions,PointsLedger,TempVideo,VideoSummary
from schemas import Points,Transaction
from database import get_db
from decimal import Decimal 
from dashboard.ai_stuff.video_summary import VideoSummarizer
from models import User,ImageMetadata,Transactions,PointsLedger,TempVideo
from schemas import Points,Transaction
from database import get_db
from faster_whisper import WhisperModel
from decimal import Decimal
import asyncio
import os
import json
from typing import Optional,Annotated
import cv2

# Learn about webauthn library, fido and passkeys
os.chdir(os.getcwd())
templates = Jinja2Templates(directory="templates")
router = APIRouter()


def extract_thumbnail_opencv(video_path, output_path, time_sec=1):
    """Extracts a thumbnail from the video using OpenCV."""
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_number = int(time_sec * fps)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video.read()
        video.release()

        if not ret:
            print("Error: Could not read frame.")
            return False

        cv2.imwrite(output_path, frame)
        print(f"Thumbnail extracted successfully to {output_path}")
        return True
    except Exception as e:
        print(f"Error extracting thumbnail: {e}")
        return False
    
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
            
            if file.size/(1024*1024) > 10:
               raise HTTPException(status_code=500,detail="Image is larger than 10 MB")
            
            contents = file.file.read()
            with open(f"static/images/{file.filename}","wb") as f:
                f.write(contents)
            user = db.query(User).filter(User.username == current_user.username).first()
            file_name = file.filename
            file_path = f"static/images/{file.filename}"
            file_size_kb = os.stat(file_path).st_size/1024
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
async def get_videos(request:Request,current_user: User = Depends(get_current_user_id),db:Session = Depends(get_db)):
        try:   
               if not current_user:
                    raise HTTPException(
                         status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="noauth",
                         headers = {"WWW-Authenticate": "Bearer"}
                    )
               videos = db.query(TempVideo).filter(TempVideo.user_id == current_user.id).all()
               print("Videos",videos)
               if not videos:
                    return RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
               else:
                    video_json = [{"title":videos[i].filename.replace(".mp4",""),"videoId":videos[i].id,"duration":0,"description":"","duration":"","thumbnailUrl":videos[i].thumbnail_path,"views":"0","likes":"0","href":f"videos/{videos[i].id}"} for i in range(len(videos))]
                    return templates.TemplateResponse("components/video_dashboard.html",{"request":request,"user":current_user,"videos":video_json})
        except HTTPException as e:
               if e.detail == "noauth":
                    return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)
               else:
                    return {"error":f"{e.detail}"}
              
@router.get("/dashboard/videos/{video_id}")
async def get_videos(request:Request ,video_id:Optional[int]=None,current_user: User = Depends(get_current_user_id),db:Session = Depends(get_db)):
        try:   
               print("Current_user",current_user)
               if not current_user:
                    raise HTTPException(
                         status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="noauth",
                         headers = {"WWW-Authenticate": "Bearer"}
                    )
      
               video = db.query(TempVideo).filter(TempVideo.id == video_id).first()
               # if not video:
               #     return RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
               # else:
               default_video = f"videos/{video.filename}" if video else None
               return templates.TemplateResponse("components/analyze_video.html",{"request":request,"user":current_user,"default_video":default_video})
        except HTTPException as e:
               if e.detail == "noauth":
                    return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)
               else:
                    return {"error":f"{e.detail}"}
              
@router.post("/video-upload")
def uploaded_video(video_file: Annotated[UploadFile,File()],current_user: User = Depends(get_current_user),thumbnail_bool:Annotated[Optional[bool],Form()]=False,db:Session = Depends(get_db)):
     try:
          if not current_user:
               raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="noauth",
                    headers = {"WWW-Authenticate": "Bearer"}
               )
          
          if video_file.size/(1024*1024) > 100:
               raise HTTPException(status_code=500,detail="Video file is larger than 100 MB")
          

          contents = video_file.file.read()

          file_path = f"static/videos/{video_file.filename}"

          if thumbnail_bool:
               thumbnail_path = f"static/video_thumbs/{video_file.filename.replace('.mp4','_thumb_1.jpg')}"
               if not extract_thumbnail_opencv(file_path,thumbnail_path):
                    raise HTTPException(status_code=500,detail="Error extracting thumbnail")
          else:
               thumbnail_path = f"static/video_thumbs/default_thumb.jpg"
          with open(file_path,"wb") as f:
               f.write(contents)

          user = db.query(User).filter(User.username == current_user.username).first()
          filename = video_file.filename
          file_size_kb = os.stat(file_path).st_size/1024

        
        
          new_video = TempVideo(user_id=user.id,filename=filename,file_path=file_path,file_size_kb=file_size_kb,thumbnail_path=f"/{thumbnail_path}")
          db.add(new_video)

          db.commit()
          db.refresh(new_video)
          db.close()
     except HTTPException as e:
          if e.detail == "noauth":
               return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)
          else:
               return {"error":f"{e.detail}"}
     finally:
          video_file.file.close()
          return RedirectResponse(url="/dashboard/videos",status_code=status.HTTP_303_SEE_OTHER)

@router.get("/dashboard/summary_{video_id}/{user_id}")
async def get_summary(request:Request,video_id:int,user_id:int,current_user: User = Depends(get_current_user_id),db:Session = Depends(get_db)):
     try:
          if not current_user:
               raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="noauth",
                    headers = {"WWW-Authenticate": "Bearer"}
                              )
          video_s = db.query(VideoSummary).filter(VideoSummary.user_id == user_id).filter(VideoSummary.video_id == video_id).first()
          if not video_s:
               return RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
          else:
               return templates.TemplateResponse("components/video_summary.html",{"request":request,"user":current_user,"video_summary":video_s.video_summary,"video_path":video_s.video_path})
     except HTTPException as e:
          if e.detail == "noauth":
               return RedirectResponse(url="/login?err=noauth",status_code=status.HTTP_303_SEE_OTHER)
          else:
               return {"error":f"{e.detail}"}
# @router.post("/analyze-video")
# async def analyze_video(request:Request,background_tasks:BackgroundTasks,analyze_video:str  = Form(...),prompt:str = Form(...),current_user:User = Depends(get_current_user),db:Session = Depends(get_db)):
     
#      if not current_user:
#           return None
    
  
#      video_path  = f"static/{analyze_video}"

#      model = "llama3.2:1b"

#      video_summarizer = VideoSummarizer(video_path=video_path,model=model,prompt=prompt)
#      try:
#          current_summary,time_in_sec = video_summarizer.analyze_video()
#      #     current_video = db.query(TempVideo).filter(TempVideo.file_path == video_path).first()
#      #     new_summary = VideoSummary(user_id=current_video.user_id,video_id=current_video.id,video_summary=current_summary)
# #   db.add(new_summary)
# #   db.commit()
#          print("Summary",current_summary)
#          return {"elapsed_time":time_in_sec,"status":"success"}
#      except Exception as e:
#           raise HTTPException(status_code=500, detail=f'Something went wrong {e}')

@router.websocket("/ws/analyze")
async def analyze_video(websocket:WebSocket,current_user:User=Depends(get_current_user_websocket),db:Session=Depends(get_db)):
     
     try:
          if not current_user:
               raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="noauth",
                    headers = {"WWW-Authenticate": "Bearer"}
               )
     


          model = "llama3.2:1b"
          print(current_user)

          
          try:
               data = json.loads(await websocket.receive_text())
               
               video_path  = f"static/{data["video_path"]}"
               print("VVVV",video_path)
               video_summarizer = VideoSummarizer(video_path=video_path,model=model,prompt=data["prompt"])

               task = asyncio.create_task(video_summarizer.analyze_video(websocket))

               while not task.done():
                    await asyncio.sleep(0.1)
          except WebSocketDisconnect:
               print("Client disconnected - canceling task")
               task.cancel()
          # except Exception as e:
          #     await websocket.send_json({"status":"error","message":str(e)})
          #     await websocket.close()
               
          #     current_summary,time_in_sec 
          #     current_video = db.query(TempVideo).filter(TempVideo.file_path == video_path).first()
          #     new_summary = VideoSummary(user_id=current_video.user_id,video_id=current_video.id,video_summary=current_summary)
     #   db.add(new_summary)
     #   db.commit()
          #     print("Summary",current_summary)
          #     return {"elapsed_time":time_in_sec,"status":"success"}
          except Exception as e:
               raise HTTPException(status_code=500, detail=f'Something went wrong {e}')
          finally:
               current_video = db.query(VideoSummary).filter(VideoSummary.video_path == video_path).first()

               await websocket.send_text(f"REDIRECT:/dashboard/summary_{current_video.id}/{current_video.user_id}")

               await websocket.close()
     except HTTPException as e:
          if e.detail == "noauth":
               await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
          else:
               await websocket.send_json({"error":f"{e.detail}"})
               await websocket.close()
