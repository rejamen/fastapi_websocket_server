from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    _env_file = "./.env"

    TEMPLATES_FOLDER_PATH: str


settings = Settings()