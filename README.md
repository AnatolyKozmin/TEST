## FCL Telegram Mini App

Стек: **FastAPI + Vue (Vite) + Redis + Postgres + aiogram-бот**.

### Быстрый старт (Docker)

1) Скопируйте env:

```
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env
```

2) Впишите токен бота в `backend/.env`:

```
BOT_TOKEN=123:abc
```

И в `bot/.env` тоже (`BOT_TOKEN`) + ссылку на мини‑апп (`WEBAPP_URL`, обязательно HTTPS в реальном Telegram).

3) Запуск:

```
docker compose up --build
```

### URLs

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/api/health`

### Запуск на сервере (самый простой прод)

Если у тебя **домен + SSL уже есть** и текущий nginx на сервере не нужен — проще всего поднять nginx **вместе с проектом**.

1) Подготовь env:

```
cp backend/.env.example backend/.env
cp bot/.env.example bot/.env
```

В `backend/.env`:
- `BOT_TOKEN=...`
- `CORS_ORIGINS=https://ВАШ_ДОМЕН`

В `bot/.env`:
- `BOT_TOKEN=...`
- `WEBAPP_URL=https://ВАШ_ДОМЕН`

2) Положи сертификаты в:

```
deploy/nginx/certs/fullchain.crt
deploy/nginx/certs/privkey.key
```

3) Запуск prod-compose:

```
docker compose -f docker-compose.prod.yml up -d --build
```

Если на сервере уже заняты 80/443 — сначала останови старые контейнеры nginx, чтобы освободить порты.

### Важно про Telegram WebApp

API требует заголовок `X-Telegram-Init-Data` (Telegram автоматически передаёт его в mini app).
Для локальной отладки можно передать `initData` через query string, фронт подхватит `?initData=...`.

