from fastapi import FastAPI
from app.api import buses, realtime


app = FastAPI()

app.include_router(buses.router)
app.include_router(realtime.router)