from pydantic import BaseModel,EmailStr,ConfigDict
# from sqlalchemy import Boolean
from datetime import datetime

class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str
    referral_code: str
    is_activated: bool
    activation_token: str
    token_expires_at: datetime


class UserResponse(BaseModel):

    username: str
    email: EmailStr
    password: str
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Token(BaseModel):
    
    access_token: str
    token_type: str


class ForgetPasswordRequest(BaseModel):
    email: str

class ResetForgetPassword(BaseModel):
    
    new_password: str
    confirm_password: str

class SuccessMessage(BaseModel):
    
    success: bool
    status_code: int 
    message: str


class EmailTemplateSchema(BaseModel):

    username: str
    link_expiry_min: str
    reset_link: str

class User(BaseModel):
    username: str