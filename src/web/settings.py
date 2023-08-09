from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_secret_key: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
