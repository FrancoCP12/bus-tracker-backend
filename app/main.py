from fastapi import FastAPI
from app.api import buses, realtime, locations, route

app = FastAPI(
    title="Bus Tracker API",
    description="Sistema de seguimiento de autobuses en tiempo real",
    version="1.0.0"
)

app.include_router(buses.router)
app.include_router(realtime.router)
app.include_router(locations.router)
app.include_router(route.router)
