import os

class Settings:
    DB_URI: str = os.getenv("DB_URI")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

settings = Settings()
