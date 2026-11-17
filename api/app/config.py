"""Configuration lue uniquement depuis l'environnement (Twelve-Factor).

En local : fichier .env (copié depuis .env.example).
Sur Scalingo : variables d'environnement de l'app (aucun secret dans Git).
"""

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Scalingo fournit SCALINGO_POSTGRESQL_URL ; en local on utilise DATABASE_URL.
    database_url: str = Field(validation_alias=AliasChoices("SCALINGO_POSTGRESQL_URL", "DATABASE_URL"))
    jwt_secret: str = Field(min_length=32)
    jwt_expire_minutes: int = 60
    # Liste d'origines séparées par des virgules (URL publique du client).
    cors_origins: str = "http://localhost:5173"

    @field_validator("database_url")
    @classmethod
    def normalize_scheme(cls, v: str) -> str:
        # Scalingo donne postgres://… ; SQLAlchemy + psycopg 3 attend postgresql+psycopg://…
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+psycopg://" + v[len(prefix) :]
        if v.startswith("sqlite"):
            raise ValueError("SQLite est interdit : utilisez PostgreSQL")
        return v

    @property
    def cors_list(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
