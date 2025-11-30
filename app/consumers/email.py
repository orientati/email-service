import json
import logging

from aio_pika import IncomingMessage

from app.schemas.email import EmailRequest
from app.services.email import send_email

logger = logging.getLogger(__name__)


async def on_email_message(message: IncomingMessage):
    """
    Callback che gestisce i messaggi dalla coda 'email'.
    Agisce come un controller: valida l'input e chiama il service.
    """
    async with message.process():
        try:
            body = message.body.decode()
            data = json.loads(body)

            payload = data.get("data", data)

            logger.info(f"Ricevuto task email per: {payload.get('to', 'unknown')}")

            # Validazione (Pydantic)
            # Se il JSON è malformato, Pydantic solleva eccezione e il messaggio va in Dead Letter (o scartato)
            email_request = EmailRequest(**payload)

            # Chiamata al Service
            result = await send_email(email_request)

            if result.code != 200:
                logger.error(f"Errore invio service: {result.detail}")
            else:
                logger.info(f"Email inviata con successo via RabbitMQ")

        except Exception as e:
            logger.error(f"Errore critico consumatore email: {e}", exc_info=True)
