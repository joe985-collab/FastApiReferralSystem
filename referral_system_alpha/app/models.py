from sqlalchemy import Column, Integer,String, Boolean,DateTime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base
from sqlalchemy.sql import func

class User(Base):

    __tablename__ = "Users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,nullable=False)
    email = Column(String,unique=True,nullable=False)
    password = Column(String,nullable=False)
    referral_code = Column(String,unique=True,nullable=True)
    referred_by = Column(String,nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),server_default=func.now())
    is_verified = Column(Boolean,default=False)
    last_active = Column(TIMESTAMP(timezone=True),nullable=True)

class ImageMetadata(Base):
     
     __tablename__ = "ImageMetadata"

     id = Column(Integer,primary_key=True,index=True)
     user_id = Column(Integer,unique=True,nullable=False)
     file_name = Column(String(255))
     file_path = Column(String(255))
     file_size_kb = Column(String(255))
     created_date = Column(TIMESTAMP(timezone=True),server_default=func.now())

class VerifyOTP(Base):

    __tablename__ = "VerifyOTP"

    id = Column(Integer,primary_key=True,index=True)
    hashed_otp = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),server_default=func.now())
    expires_at = Column(DateTime)

class ReferralTableM(Base):

     __tablename__ = "ReferralTable"

     id = Column(Integer,primary_key=True,index=True)
     referrer_id = Column(Integer,nullable=False)
     referred_user_id = Column(Integer,unique=True,nullable=False)
     date_referred = Column(TIMESTAMP(timezone=True),server_default=func.now())
     status = Column(String,nullable=True)


