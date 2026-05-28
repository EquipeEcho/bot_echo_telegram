import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger
import sys

# Configure Loguru
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", rotation="10 MB", level="DEBUG")

class Settings(BaseSettings):
    telegram_token: str
    group_id: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

try:
    settings = Settings()
except Exception as e:
    logger.critical(f"Missing required environment variables: {e}")
    sys.exit(1)

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.post("/echo_webhook")
async def handle_echo_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON received: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if "commits" in payload:
        repository = payload.get("repository", {}).get("full_name", "unknown").replace('_', '\\_')
        for commit in payload.get("commits", []):
            author = commit.get("author", {}).get("name", "Unknown")
            username = commit.get("author", {}).get("username", "Unknown")
            message = commit.get("message", "No message")
            url = commit.get("url", "#")

            text = (
                f"🚀 **Novo Commit em {repository}**\n\n"
                f"📝 {message}\n"
                f"👤 Autor: {author}\n"
                f"Username: {username}\n"
                f"🔗 [Ver no GitHub]({url})"
            )

            await send_telegram_message(text)

    return {"status": "success"}

@app.post("/jira-webhook")
async def jira_webhook(request: Request):
    try:
        data = await request.json()
        issue = data.get("issue", {})
        fields = issue.get("fields", {})

        titulo = fields.get("summary", "Sem título")
        status = fields.get("status", {}).get("name", "Sem status")
        responsavel = fields.get("assignee", {}).get("displayName", "Não atribuído")
        chave = issue.get("key", "")

        mensagem = (
            f"📌 Novo evento no Jira\n\n"
            f"🔑 {chave}\n"
            f"📄 {titulo}\n"
            f"📊 Status: {status}\n"
            f"👤 Responsável: {responsavel}"
        )

        await send_telegram_message(mensagem)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Jira webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Error")

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json={
                "chat_id": settings.group_id,
                "text": text,
                "parse_mode": "Markdown"
            })
            response.raise_for_status()
            logger.info(f"Telegram message sent: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
