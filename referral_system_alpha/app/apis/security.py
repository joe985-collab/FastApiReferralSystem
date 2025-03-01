from datetime import datetime,timezone
from datetime import timedelta
from typing import Optional
from dotenv import load_dotenv

from jose import jwt

load_dotenv(".env")
import os

secret_key = os.getenv("SECRET_KEY")

def create_access_token(data: dict,expires_delta: Optional[timedelta] = None):
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, str(secret_key),algorithm="HS256"
    )

    return encoded_jwt