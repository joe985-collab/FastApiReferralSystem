from pydantic import BaseModel,EmailStr,ConfigDict
# from sqlalchemy import Boolean
from datetime import datetime
from typing import Optional
from decimal import Decimal

class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()

class ReferralTable(BaseModel):

    referrer_id: int
    referred_user_id: int
    date_referred: Optional[datetime] = datetime.now()
    status: Optional[str] = None
    
class UserResponse(BaseModel):

    username: str
    email: EmailStr
    password: str
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Image:

    user_id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size_kb: Optional[str] = None
    
class Token(BaseModel):
    
    access_token: str
    token_type: str

class Points(BaseModel):

    user_id:int
    points: int
    type: str
    expires_at: datetime
    reference_id: Optional[int] = None
    created_at: datetime

class Transaction(BaseModel):

    user_id: int
    amount: Decimal
    status: str
    created_at: Optional[datetime] = datetime.now()

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetForgetPassword(BaseModel):
    
    new_password: str
    confirm_password: str

class SuccessMessage(BaseModel):
    
    success: bool
    status_code: int 
    message: str

class VerifyOTP(BaseModel):

    hashed_otp: str
    expires_at: str

class EmailTemplateSchema(BaseModel):

    username: str
    link_expiry_min: str
    reset_link: str

class User(BaseModel):
    username: str