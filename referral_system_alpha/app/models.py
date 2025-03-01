from sqlalchemy import Column, Integer,String, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base

class User(Base):

    __tablename__ = "Users"

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,nullable=False)
    email = Column(String,unique=True,nullable=False)
    password = Column(String,nullable=False)
    referral_code = Column(String,unique=True)
    referred_by = Column(String)
    created_at = Column(TIMESTAMP(timezone=True))