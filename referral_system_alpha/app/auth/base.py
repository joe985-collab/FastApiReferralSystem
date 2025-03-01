from auth import route_login, route_register
from fastapi import APIRouter


api_router_auth = APIRouter()
api_router_auth.include_router(route_login.router,prefix="",tags=["webapp-login"])
api_router_auth.include_router(route_register.router,prefix="",tags=["webapp-register"])