from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://insightops:insightops@localhost:5432/insightops"
    jwt_secret: str = "change-me"
    jwt_ttl_minutes: int = 720
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

settings = Settings()
