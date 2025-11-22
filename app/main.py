from __future__ import annotations

import sys
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.httpx import HttpxIntegration

from app.api.v1.routes import email
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services import broker

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    send_default_pii=True,
    enable_tracing=True,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    profiles_sample_rate=1.0,
    enable_logs=True,
    integrations=[HttpxIntegration()],
    release=settings.SENTRY_RELEASE
)

sentry_sdk.set_tag("service.name", settings.SERVICE_NAME)
logger = None


# RabbitMQ Broker
async def callback(message):
    async with message.process():
        print(
            f"Received message from exchange '{message.exchange}' with routing key '{message.routing_key}': {message.body.decode()}")


# TODO: gestire logica invio email tramite rabbitMQ

exchanges = {
    "email": callback,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.SERVICE_NAME}...")

    # Avvia il broker asincrono all'avvio dell'app
    broker_instance = broker.AsyncBrokerSingleton()
    connected = await broker_instance.connect()
    if (not connected):
        logger.error("Could not connect to RabbitMQ. Continuing without broker...")
        # sys.exit(1)
        # return

    else:
        logger.info("Connected to RabbitMQ.")
        for exchange, cb in exchanges.items():
            await broker_instance.subscribe(exchange, cb)

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
