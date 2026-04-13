from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    sendgrid_api_key: str
    from_email: str = "noreply@cybershield.az"
    base_url: str = "http://localhost:8000"
    access_token_expire_minutes: int = 60 * 8  # 8 saat

    class Config:
        env_file = ".env"


settings = Settings()
