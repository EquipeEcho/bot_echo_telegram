import httpx
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    telegram_token: str
    group_id: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

try:
    settings = Settings()
except Exception as e:
    logger.error(f"Missing required environment variables: {e}")
    raise

app = FastAPI()

@app.post("/echo_webhook")
async def handle_echo_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
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

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id": settings.group_id,
                "text": text,
                "parse_mode": "Markdown"
            })
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        logger.error(f"Failed to send telegram message: {e}")
        return None