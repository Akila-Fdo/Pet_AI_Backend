# Docker Run Guide

## What to use

Use the root `docker-compose.yml` file from `E:\rag_petpulse\Pet_AI_Backend`.

## Build and start

```bash
docker-compose up --build -d
```

## View logs

```bash
docker-compose logs -f fastapi
docker-compose logs -f chatbot
```

## Stop

```bash
docker-compose down
```

## Run ingestion once

```bash
docker-compose run --rm chatbot python chatbot/scripts/ingest_documents.py
```

## Notes

- Run the command from the repository root: `E:\rag_petpulse\Pet_AI_Backend`.
- Keep `.env` in the root directory so Compose can load it.
- If you want to re-create the env file from scratch, use the existing `.env` in the repo root as the source of truth.
