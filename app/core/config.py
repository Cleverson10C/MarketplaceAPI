import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "2"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admin:zHLaVPULpPbqmHQHXDUiIGjQCE6oyvd7@dpg-d8n9gl4m0tmc73dsqh2g-a.oregon-postgres.render.com/marketplace_api_render",
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
