from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Evaluation Sheet API"
    app_version: str = "1.0.0"
    cors_origins: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # Database
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_name: str = "evaluation_sheet"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def database_url_sync(self) -> str:
        """URL cho Alembic migrations (sync driver)."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
