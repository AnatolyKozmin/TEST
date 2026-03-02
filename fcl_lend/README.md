# FCL Landing Page

Лендинг для Financial Cybersport League (FCL/SCL 26)

## Локальная разработка

```bash
npm install
npm run dev
```

## Сборка

```bash
npm run build
```

## Деплой на GitHub Pages

Проект автоматически деплоится на GitHub Pages при пуше в ветку `main` или `master` через GitHub Actions.

### Настройка GitHub Pages

1. Перейди в Settings → Pages твоего репозитория
2. В разделе "Source" выбери "GitHub Actions"
3. После первого пуша в main/master workflow автоматически соберёт и задеплоит проект

### Важно

Если репозиторий называется не `fcl_lend`, нужно обновить `base` в `vite.config.js`:

```js
base: process.env.GITHUB_ACTIONS ? '/имя-твоего-репо/' : '/',
```
