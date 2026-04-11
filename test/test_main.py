from unittest.mock import MagicMock, patch

import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from src.main import app, send_telegram_message
from unittest.mock import patch, AsyncMock

load_dotenv('.env')


testclient = TestClient(app)


def test_receber_post():
    payload = {
        "repository": {
            "full_name": "username/repo"
        },
        "commits": [
            {
                "author": {"name": "Test User"},
                "message": "test: this is a test",
                "url": "https://github.com/username/repo/commit/123456"
            }
        ]
    }

    response = testclient.post(
        '/echo_webhook',
        json=payload
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_jira_webhook():
    payload = {
        "webhookEvent": "jira:issue_created",
        "issue": {
            "key": "TEST-123",
            "fields": {
                "summary": "Bug no login",
                "status": {"name": "To Do"},
                "assignee": {"displayName": "Fabio"}
            }
        }
    }

    with patch("src.main.send_telegram_message", new_callable=AsyncMock) as mock_send:
        response = testclient.post('/jira-webhook', json=payload)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        mock_send.assert_called_once()

        args, kwargs = mock_send.call_args
        mensagem = args[0]

        assert "TEST-123" in mensagem
        assert "Bug no login" in mensagem
        assert "To Do" in mensagem

@pytest.mark.asyncio
async def test_send_telegram_message_mock():
    # Criamos um "boneco" de resposta que simula o httpx.Response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'ok': True}

    # Interceptamos a chamada do post dentro do httpx
    with patch("httpx.AsyncClient.post", return_value=mock_response):
        from src.main import send_telegram_message
        
        response = await send_telegram_message('TEST_MESSAGE', 'fake_token', 'fake_id')

        assert response.status_code == 200
        assert response.json()['ok'] is True