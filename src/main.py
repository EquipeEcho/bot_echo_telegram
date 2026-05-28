import httpx
from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()

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

# Cria a função  para a notificação dos eventos do Jira
@app.post("/jira-webhook")
async def jira_webhook(request: Request):
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

    print(mensagem)

    await send_telegram_message(mensagem)

    return {"status": "ok"}

async def send_telegram_message(text: str, token=TELEGRAM_TOKEN, group_id=GROUP_ID):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "chat_id": group_id,
            "text": text,
            "parse_mode": "Markdown"
        })

        print("Status Telegram:", response.status_code)
        print("Resposta Telegram:", response.text)

        return response