from apis import route_login
from fastapi import APIRouter


api_router_apis = APIRouter()
api_router_apis.include_router(route_login.router,prefix="/login",tags=["login"])