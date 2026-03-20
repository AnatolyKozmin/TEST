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

### Локальный запуск лендинга для тестов

Лендинг можно поднять отдельно в dev-режиме (с hot reload) через профиль `landing`:

```
docker compose --profile landing up landing
```

После запуска лендинг будет доступен по адресу:

- `http://127.0.0.1:5174`

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
- `WEBAPP_URL=https://ВАШ_ДОМЕН/tma/`

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

### Бот «молчит» / не отвечает на `/start`

1. **Логи контейнера:** `docker compose logs -f bot` (или `docker compose -f docker-compose.prod.yml logs -f bot`). Должна быть строка `Polling started; webapp ...`. Ошибки `Unauthorized` — неверный `BOT_TOKEN`; `Conflict` — второй процесс с тем же токеном (другой сервер или локальный запуск).
2. **Webhook:** если раньше включали webhook, polling не получает апдейты. В коде бота перед стартом вызывается `delete_webhook`; пересоберите образ и перезапустите бота.
3. **`bot/.env`:** обязательны `BOT_TOKEN` и корректный `WEBAPP_URL` (HTTPS для прод). Без валидного токена контейнер может сразу падать при старте.
4. **SSL к Telegram:** если в логах `Cannot connect to host api.telegram.org:443` или «SSL handshake» дольше 60 с — с сервера нет нормального выхода к API Telegram (фаервол, блокировка, часто **битый IPv6**). Проверка: `curl -4 -I https://api.telegram.org` (форс IPv4). На хосте можно временно отключить IPv6 для теста; бот при старте теперь **ждёт** доступность API с повторными попытками, а не падает сразу.

### Важно про Telegram WebApp

API требует заголовок `X-Telegram-Init-Data` (Telegram автоматически передаёт его в mini app).
Для локальной отладки можно передать `initData` через query string, фронт подхватит `?initData=...`.

### Разделение Landing и Mini App

- `https://ВАШ_ДОМЕН/` -> landing (без Telegram SDK)
- `https://ВАШ_ДОМЕН/tma/` -> Telegram Mini App
- `https://ВАШ_ДОМЕН/api/` -> backend API

