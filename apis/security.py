from datetime import datetime,timezone
from datetime import timedelta
from typing import Optional
from dotenv import load_dotenv

from jose import jwt,JWTError

import os
load_dotenv(os.path.join('apis', '.env'))


SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))


def create_access_token(data: dict,expires_delta: Optional[timedelta] = None):
    
    to_encode = data.copy()
    if not expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    else:
        expire = expires_delta
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY,ALGORITHM
    )

    return encoded_jwt

def get_exp_token(token:str):
      try:
         payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
         return datetime.fromtimestamp(payload.get("exp"))
      except JWTError as e:
         print("error",e)
      
def decode_token(token: str):
      try:
         payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
         id: int = payload.get("sub")
         return id
      except JWTError as e:
         print("error",e)
