import json
import logging

from aio_pika import IncomingMessage

from app.schemas.email import EmailRequest
from app.services.email import send_email
from app.core.logging import get_logger

logger = get_logger(__name__)


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
            email_request = EmailRequest(**payload)

            # Chiamata al Service
            # Se send_email fallisce, solleva eccezione e message.process() farà il nack (requeue)
            result = await send_email(email_request)
            
            logger.info(f"Email inviata con successo via RabbitMQ: {result.detail}")

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            # Errori di validazione o input malformato: NON riprovare.
            # Uscendo dal blocco try senza sollevare eccezione, il context manager farà ack.
            logger.error(f"Errore validazione/input task email: {e}. Messaggio scartato.")
        except Exception as e:
            # Errori transitori (es. connessione SMTP): Riprova (Nack + Requeue)
            logger.error(f"Errore critico invio email: {e}. Il messaggio verrà riaccodato.", exc_info=True)
            raise e
