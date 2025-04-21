from dashboard import route_dashboard
from fastapi import APIRouter


api_router_dashboard = APIRouter()
api_router_dashboard.include_router(route_dashboard.router,prefix="",tags=["webapp-dashboard"])