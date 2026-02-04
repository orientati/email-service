from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "email_service"
    SERVICE_VERSION: str = "0.1.0"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_SEND_EMAIL_ROUTING_KEY: str = "email_queue"
    RABBITMQ_CONNECTION_RETRIES: int = 5
    RABBITMQ_CONNECTION_RETRY_DELAY: int = 5
    SERVICE_PORT: int = 8000
    ENVIRONMENT: str = "development"
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "local"
    SENTRY_DEBUG: bool = False
    SENTRY_RELEASE: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    MAIL_FROM_NAME: str = ""
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EMAIL_",
        extra="ignore"
    )


settings = Settings()
