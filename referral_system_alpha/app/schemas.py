from pydantic import BaseModel,EmailStr,ConfigDict

class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):

    username: str
    email: EmailStr
    password: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Token(BaseModel):
    
    access_token: str
    token_type: str