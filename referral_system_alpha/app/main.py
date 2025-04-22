from fastapi import FastAPI,Depends,Request
from sqlalchemy.orm import Session
import models
from database import engine
import schemas
from apis.base import api_router_apis
from auth.base import api_router_auth
from dashboard.base import api_router_dashboard
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from auth.TwoFA_Session import backend,cookie,verifier
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
load_dotenv(os.path.join('apis', '.env'))


SESSION_KEY = str(os.getenv("SESSION_KEY"))

def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def create_tables(): 
        models.Base.metadata.create_all(bind=engine)

def include_router(app):
        app.include_router(api_router_apis)
        app.include_router(api_router_auth)
        app.include_router(api_router_dashboard)
        
def start_application():

        app = FastAPI()
        # app.add_middleware(SessionMiddleware, secret_key=SESSION_KEY,session_cookie="session_cookie",max_age=1800)
        create_tables()
        configure_static(app)
        include_router(app)
        return app

app = start_application()

@app.exception_handler(404)
async def not_found_exception_handler(request:Request,exc:HTTPException):
       return RedirectResponse(url="/login")

# @app.post("/users/",response_model=schemas.UserResponse,status_code=201)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        
#         hashed_password = Hasher.hash_password(user.password)
#         # new_user = models.User(**user.model_dump())
#         new_user = models.User(username=user.username,email=user.email,password=hashed_password)
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user
