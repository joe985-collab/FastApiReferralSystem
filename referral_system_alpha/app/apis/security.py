from datetime import datetime,timezone
from datetime import timedelta
from typing import Optional
from dotenv import load_dotenv

from jose import jwt,JWTError

import os
load_dotenv(os.path.join('apis', '.env'))


SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))
print("**************")
print(SECRET_KEY)
print(ALGORITHM)
print("*************")

def create_access_token(data: dict,expires_delta: Optional[timedelta] = None):
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY,ALGORITHM
    )

    return encoded_jwt

def decode_token(token: str):
      try:
         payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
         email: str = payload.get("sub")
         return email
      except JWTError:
         return None