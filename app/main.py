from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import buses, realtime, locations, route

app = FastAPI(
    title="Bus Tracker API",
    description="Sistema de seguimiento de autobuses en tiempo real",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(buses.router)
app.include_router(realtime.router)
app.include_router(locations.router)
app.include_router(route.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Bus Tracker API running"}
