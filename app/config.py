from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://marketplace_user:marketplace_pass@localhost:5432/marketplace_db"
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
