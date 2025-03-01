from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
import models
from database import engine
import schemas
from apis.base import api_router_apis
from auth.base import api_router_auth
from fastapi.staticfiles import StaticFiles


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def create_tables(): 
        models.Base.metadata.create_all(bind=engine)

def include_router(app):
        app.include_router(api_router_apis)
        app.include_router(api_router_auth)

def start_application():

        app = FastAPI()
        configure_static(app)
        include_router(app)
        return app

app = start_application()
# @app.post("/users/",response_model=schemas.UserResponse,status_code=201)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        
#         hashed_password = Hasher.hash_password(user.password)
#         # new_user = models.User(**user.model_dump())
#         new_user = models.User(username=user.username,email=user.email,password=hashed_password)
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user
