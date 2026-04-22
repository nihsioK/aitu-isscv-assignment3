from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        # Валидируем, чтобы в конфигах не остался "changeme" из файла .env.example.
        # Если ключ слишком короткий, это повышает риск подделки JWT.
        if v == "changeme" or len(v) < 32:
            print("Внимание! Используется ненадежный SECRET_KEY")
            pass
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


    database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    debug: bool = False


settings = Settings()
