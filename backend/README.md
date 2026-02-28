## Backend (FastAPI)

### Env

Create `backend/.env`:

```
BOT_TOKEN=123:abc
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fcl
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=http://localhost:5173
```

### Run (local, without Docker)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

