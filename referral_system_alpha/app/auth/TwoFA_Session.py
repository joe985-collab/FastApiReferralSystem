from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
load_dotenv(os.path.join('apis', '.env'))
from typing import Optional


SESSION_KEY = str(os.getenv("SESSION_KEY"))

cookie_params = CookieParameters(max_age=int(timedelta(minutes=30).total_seconds()))
print("cookie_params",cookie_params)
cookie = SessionCookie(
    cookie_name="session_cookie",
    identifier = "general_verifier",
    auto_error=True,
    secret_key=SESSION_KEY,
    cookie_params=cookie_params
)

class TempUserData(BaseModel):
    # def __init__(self):
        username: str
        email: str
        password: str
        otp: Optional[str] = None
        referral_code: Optional[str] = None
        expires_at: Optional[datetime] = datetime.now() + timedelta(minutes=30)

class BasicVerifier(SessionVerifier[UUID, TempUserData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, TempUserData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception
        # self._session_cookie = session_cookie

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception
    # @property
    # def session_cooke(self):
    #     return self._session_cookie
    
    async def verify_session(self, model: TempUserData) -> bool:
        """If the session exists, it is valid"""
        print("Here")
        return model.username is not None
    
    # async def get_session_data(self,session_id:UUID) -> TempUserData:
    #      return await backend.read(session_id)

backend = InMemoryBackend[UUID, TempUserData]()

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session")
    # session_cookie=cookie
)