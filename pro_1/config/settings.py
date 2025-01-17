import os

class Settings:
    DB_URI: str = os.getenv("DB_URI")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    
    
    
    
    # Check for missing environment variables
    if not DB_URI or not SECRET_KEY:
        raise ValueError("Missing required environment variables: DB_URI or SECRET_KEY")


settings = Settings()
