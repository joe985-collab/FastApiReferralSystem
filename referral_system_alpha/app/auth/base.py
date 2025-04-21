from auth import route_login, route_register, route_password_forget
from fastapi import APIRouter


api_router_auth = APIRouter()
api_router_auth.include_router(route_login.router,prefix="",tags=["webapp-login"])
api_router_auth.include_router(route_register.router,prefix="",tags=["webapp-register"])
api_router_auth.include_router(route_password_forget.router,prefix="",tags=["webapp-forget"])
