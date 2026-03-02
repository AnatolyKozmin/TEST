# Инструкция по деплою на GitHub Pages

## Вариант 1: Проект в подпапке (текущая структура)

Если твой проект находится в папке `fcl_lend/` внутри репозитория:

1. **Убедись, что workflow файл правильный**: `.github/workflows/deploy.yml` (уже создан)

2. **Настрой base path в `vite.config.js`**:
   - Если репозиторий называется `fcl_lend` → оставь как есть
   - Если репозиторий называется по-другому → замени `/fcl_lend/` на `/имя-твоего-репо/`

3. **Включи GitHub Pages**:
   - Перейди в Settings → Pages твоего репозитория
   - В разделе "Source" выбери **"GitHub Actions"**
   - Сохрани

4. **Запушь код**:
   ```bash
   git add .
   git commit -m "Add GitHub Actions workflow"
   git push origin main
   ```

5. **Проверь деплой**:
   - Перейди в Actions → там увидишь запущенный workflow
   - После успешного выполнения сайт будет доступен по адресу:
     `https://твой-username.github.io/fcl_lend/`

## Вариант 2: Проект в корне репозитория

Если хочешь, чтобы проект был в корне репозитория:

1. **Переименуй workflow**:
   ```bash
   mv .github/workflows/deploy-simple.yml .github/workflows/deploy.yml
   rm .github/workflows/deploy.yml  # удали старый
   ```

2. **Обнови `vite.config.js`**:
   ```js
   base: process.env.GITHUB_ACTIONS ? '/имя-твоего-репо/' : '/',
   ```
   Или просто `base: '/'` если репозиторий называется `username.github.io`

3. **Включи GitHub Pages** (как в варианте 1)

4. **Запушь код**

## Проверка

После пуша:
- Зайди в **Actions** вкладку на GitHub
- Увидишь запущенный workflow "Deploy to GitHub Pages"
- Дождись завершения (обычно 2-3 минуты)
- Сайт будет доступен по адресу из шага 5 варианта 1

## Troubleshooting

**Ошибка "No such file or directory"**:
- Проверь, что в workflow правильный `working-directory` и `path`

**Сайт не открывается / 404**:
- Проверь `base` в `vite.config.js` - он должен совпадать с именем репозитория
- Убедись, что GitHub Pages включен в Settings

**Workflow не запускается**:
- Проверь, что файл `.github/workflows/deploy.yml` существует
- Проверь, что пушишь в ветку `main` или `master`
