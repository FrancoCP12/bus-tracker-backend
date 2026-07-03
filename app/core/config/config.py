import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    host_redis: str = os.getenv("HOST_REDIS", "localhost")
    port_redis: int = os.getenv("PORT_REDIS", 6379)
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    geo_srid: int = os.getenv("GEO_SRID", 4326)
    near_stop_meters: int = os.getenv("NEAR_STOP_METERS", 15)
    near_user_meters: int = os.getenv("NEAR_USER_METERS", 500)
    search_degrees: float = os.getenv("SEARCH_DEGREES", 0.0045)

    # pyrefly: ignore [unexpected-keyword]
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()