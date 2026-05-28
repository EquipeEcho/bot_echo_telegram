# Echo Bot Telemetry

Sistema de monitoramento e integração para notificações do GitHub e Jira via Telegram.

## Configuração

1. Crie um arquivo `.env` baseado no `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Preencha as variáveis de ambiente necessárias (`TELEGRAM_TOKEN`, `GROUP_ID`, `CLOUDFLARED_TOKEN`).

## Execução

Use Docker Compose para iniciar os serviços:
```bash
docker compose up -d --build
```

## Logs

Os logs do sistema são armazenados localmente na pasta `logs/` através de um volume mapeado.

## Desenvolvimento

O projeto utiliza `fastapi`, `uv` para gerenciamento de dependências e `loguru` para logging.
A integridade do container é verificada via `HEALTHCHECK` (porta 8082).
