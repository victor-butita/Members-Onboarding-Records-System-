import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Members' Onboarding & Records System (MORS)"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mors-kenya-parliament-secret-key-2027-super-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mors.db")
    
    # Uploads
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    MAX_FILE_SIZE_MB: int = 5
    
    # Portal Settings
    PORTAL_OPEN: bool = True
    REGISTRATION_YEAR: int = 2027
    PARLIAMENT_TERM: str = "14th Parliament"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
