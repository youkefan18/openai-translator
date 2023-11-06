import os
import sys
from functools import lru_cache

from pydantic_settings import BaseSettings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import LOG


class Settings(BaseSettings):
    app_name:str = "OpenAI Translation"
    ENVIRONMENT:str = "dev"
    FILESTORE_TYPE:str = "local"
    FILESTORE_URL:str = "d:/Playground/openai-translator/tests"
    DATABASE_TYPE:str = "sqlite"
    DATABASE_URL:str = "d:/Playground/openai-translator/tests/translations.db"
    class Config:
        env_file = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/{os.getenv("ENVIRONMENT", "dev")}.env'
        case_sensitive = True
        env_prefix = ""

@lru_cache()
def get_settings():
    settings = Settings()
    LOG.info((f"Loaded settings for environment: {settings.ENVIRONMENT}"))
    return settings

if __name__ == "__main__":
    print(Settings().model_dump())