import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.services import broker
from app.services.email import fast_mail

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
def mock_broker(monkeypatch):
    """
    Simula AsyncBrokerSingleton per evitare la connessione a RabbitMQ durante i test.
    """
    mock_instance = MagicMock()
    mock_instance.connect = AsyncMock(return_value=True)
    mock_instance.subscribe = AsyncMock()
    mock_instance.close = AsyncMock()
    
    # Simula il comportamento del singleton: quando viene chiamato AsyncBrokerSingleton(), restituisce mock_instance
    # Poiché AsyncBrokerSingleton è una classe, dobbiamo simulare __new__ o la classe stessa.
    # Un modo più semplice se viene utilizzato come singleton è applicare la patch alla classe nel modulo in cui viene utilizzata,
    # o meglio, applicare la patch alla classe stessa.
    
    def mock_constructor(*args, **kwargs):
        return mock_instance

    # Applichiamo la patch alla classe stessa per restituire la nostra istanza simulata
    monkeypatch.setattr(broker, "AsyncBrokerSingleton", mock_constructor)
    
    return mock_instance

@pytest.fixture(autouse=True)
def mock_templates(monkeypatch):
    """
    Simula app.services.email.templates per evitare di aver bisogno dei file template effettivi.
    """
    mock_tmpl = MagicMock()
    # Simula get_template per restituire un oggetto template simulato con un metodo render
    mock_template = MagicMock()
    mock_template.render.return_value = "<html><body>Mocked Email Content</body></html>"
    mock_tmpl.get_template.return_value = mock_template
    
    from app.services import email
    monkeypatch.setattr(email, "templates", mock_tmpl)
    return mock_tmpl

@pytest.fixture(autouse=True)
def mock_send_email(monkeypatch):
    """
    Simula fast_mail.send_message per evitare l'invio di email effettive.
    """
    mock_send = AsyncMock()
    monkeypatch.setattr(fast_mail, "send_message", mock_send)
    return mock_send
