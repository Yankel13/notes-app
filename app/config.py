from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "notes-app"
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "notes"
    postgres_password: str = "notes_secret"
    postgres_db: str = "notes_db"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    secret_key: str = "change-me"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
