"""
Configuración central del microservicio FastAPI.

Este microservicio es dueño exclusivo de la tabla Inventario
(registro, consulta, PDF, envío por correo).

No implementa autenticación propia: valida el token JWT emitido por
Django, por lo que comparte el mismo algoritmo y clave de firma vía
variables de entorno.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Aplicación ---
    APP_NAME: str = "Lite Thinking - Inventario Service"
    DEBUG: bool = True

    # --- PostgreSQL (misma base de datos única del sistema) ---
    POSTGRES_DB: str = "lite_thinking_db"
    POSTGRES_USER: str = "lite_thinking_user"
    POSTGRES_PASSWORD: str = "lite_thinking_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # --- JWT: debe coincidir con la configuración de Django ---
    JWT_ALGORITHM: str = "HS256"
    JWT_SIGNING_KEY: str = "change-this-in-real-env"

    # --- Integración con Django: FastAPI reenvía el mismo token del
    # Administrador para leer Empresa/Productos vía REST, en lugar de
    # tocar sus tablas directamente ---
    DJANGO_API_URL: str = "http://localhost:8000/api"

    # --- Envío de correo (FastAPI es dueño del envío del PDF de
    # Inventario). Si SMTP_HOST queda vacío, se usa un modo "consola"
    # que registra el correo en el log en vez de enviarlo, útil para
    # verificar el flujo sin un servidor SMTP real. ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = "inventario@lite-thinking.local"
    SMTP_FROM_NAME: str = "Lite Thinking - Inventario"

    # --- CORS ---
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Agente de IA con pgvector. Proveedor de embeddings:
    # configurable vía EMBEDDINGS_PROVIDER ("gemini" u "openai") — ver
    # docs/agente_ia_decision_proveedor.md para la comparación. Por
    # defecto se usa Gemini porque su API tiene una capa gratuita real
    # (sin tarjeta de crédito); OpenAI queda disponible como alternativa
    # si se prefiere. Si falta la clave del proveedor seleccionado, el
    # resto del servicio sigue funcionando con normalidad; solo los
    # endpoints de embeddings y búsqueda semántica responderán
    # 502 Bad Gateway.
    EMBEDDINGS_PROVIDER: str = "gemini"
    EMBEDDINGS_DIMENSION: int = 1536

    GEMINI_API_KEY: str = ""
    GEMINI_EMBEDDINGS_MODEL: str = "gemini-embedding-001"

    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
