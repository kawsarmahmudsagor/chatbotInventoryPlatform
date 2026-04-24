from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    VM_PASSWORD: str

    API_PREFIX: str = "/api"
    DEBUG: bool =False
    
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()        

