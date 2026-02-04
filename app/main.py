from __future__ import annotations

import asyncio
import sentry_sdk
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.httpx import HttpxIntegration

from app.api.v1.routes import email
from app.consumers import email as email_consumer
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services import broker

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,  # TODO Modificare in produzione
    profiles_sample_rate=1.0,  # TODO Modificare in produzione
    integrations=[HttpxIntegration()],
    environment=settings.SENTRY_ENVIRONMENT,
    debug=settings.SENTRY_DEBUG,
    release=settings.SENTRY_RELEASE,
)

sentry_sdk.set_tag("service.name", settings.SERVICE_NAME)
logger = None

exchanges = {
    "email": email_consumer.on_email_message,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.SERVICE_NAME}...")

    # Avvia il broker asincrono all'avvio dell'app
    broker_instance = broker.AsyncBrokerSingleton()
    
    # Connect ritorna False se fallisce dopo tutti i retry
    connected = await broker_instance.connect(
        retries=settings.RABBITMQ_CONNECTION_RETRIES,
        delay=settings.RABBITMQ_CONNECTION_RETRY_DELAY
    )
    
    if not connected:
        logger.error("Could not connect to RabbitMQ after multiple attempts. Exiting...")
        sys.exit(1)
    
    logger.info("Connected to RabbitMQ.")
    for exchange, cb in exchanges.items():
        await broker_instance.subscribe(exchange, cb, routing_key=settings.RABBITMQ_SEND_EMAIL_ROUTING_KEY)

    yield

    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    await broker_instance.close()
    logger.info("RabbitMQ connection closed.")


docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"

app = FastAPI(
    title=settings.SERVICE_NAME,
    default_response_class=ORJSONResponse,
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# Routers
current_router = APIRouter()

current_router.include_router(
    prefix="/email",
    tags=[settings.SERVICE_NAME, "email"],
    router=email.router,
)

app.include_router(current_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.SERVICE_NAME}
