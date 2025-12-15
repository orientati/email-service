from __future__ import annotations

from contextlib import asynccontextmanager

import sentry_sdk
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
# async def callback(message): #TODO: spostare in un servizio per rabbitmq
# async with message.process():
#     try:
#         body = message.body.decode()
#         data = json.loads(body)
#         if logger:
#             logger.info(f"Received email task: {data}")
#
#         # Si presume che il corpo del messaggio sia un JSON che corrisponde allo schema SendEmail o abbia un campo 'data'
#
#         email_data = data.get("data", data)
#
#         # Validazione tramite schema
#         from app.schemas.email import SendEmail
#         from app.services.email import send_email
#
#         email_request = SendEmail(**email_data)
#         result = await send_email(email_request)
#
#         if result.code != 200:
#             if logger:
#                 logger.error(f"Failed to send email via RabbitMQ: {result.message} - {result.detail}")
#         else:
#             if logger:
#                 logger.info(f"Email sent via RabbitMQ: {result.detail}")
#
#     except Exception as e:
#         if logger:
#             logger.error(f"Error processing RabbitMQ message: {e}")
#

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
    connected = False
    for i in range(settings.RABBITMQ_CONNECTION_RETRIES):
        logger.info(f"Connecting to RabbitMQ (attempt {i + 1}/{settings.RABBITMQ_CONNECTION_RETRIES})...")
        connected = await broker_instance.connect()
        if connected:
            break
        logger.warning(
            f"Failed to connect to RabbitMQ. Retrying in {settings.RABBITMQ_CONNECTION_RETRY_DELAY} seconds...")
        await asyncio.sleep(settings.RABBITMQ_CONNECTION_RETRY_DELAY)

    if not connected:
        logger.error("Could not connect to RabbitMQ after multiple attempts. Exiting...")
        sys.exit(1)

    else:
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
