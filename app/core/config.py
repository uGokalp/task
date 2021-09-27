from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Settings to use within the fastapi app
    Both variables are read from .env
    """

    db_uri: str = Field(..., env="MONGODB_URL")
    db_name: str = Field(..., env="DB_NAME")

    class Config:
        env_prefix = ""
        env_file = ".env"
