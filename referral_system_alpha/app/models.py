from sqlalchemy import Column, Integer,String, Boolean,DateTime,Numeric
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

class Transactions(Base):
     
     __tablename__ = "Transactions"

     id = Column(Integer,primary_key=True,index=True)
     user_id = Column(Integer,nullable=False)
     amount = Column(Numeric)
     status  = Column(String(10),nullable=False)
     created_at = Column(TIMESTAMP(timezone=True),server_default=func.now()) 

class PointsLedger(Base):
     
     __tablename__ = "PointsLedger"

     id = Column(Integer,primary_key=True,index=True)
     user_id = Column(Integer,nullable=False)
     points = Column(Integer)
     type = Column(String(10),nullable=False)
     expires_at = Column(TIMESTAMP(timezone=True),nullable=False)
     reference_id = Column(Integer)
     created_at = Column(TIMESTAMP(timezone=True),server_default=func.now()) 


class TempVideo(Base):
     
     __tablename__ = "TempVideo"

     id = Column(Integer,primary_key=True,index=True)
     user_id = Column(Integer,nullable=False)
     filename = Column(String(255),nullable=False)
     file_path = Column(String(512),nullable=False)
     file_size_kb = Column(String,nullable=False)
     created_at = Column(TIMESTAMP(timezone=True),server_default=func.now())