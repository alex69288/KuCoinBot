# 🌐 Развертывание Telegram Web App

## 📋 Архитектура

```
┌──────────────────────┐
│   GitHub Pages       │  ← Frontend (HTML/JS)
│   (бесплатно, HTTPS) │     https://username.github.io/repo
└──────────┬───────────┘
           │ CORS API запросы
           ↓
┌──────────────────────┐
│   Backend Server     │  ← Python FastAPI + Bot
│   (VPS/Cloud)        │     webapp/server.py
│   - Railway.app      │     core/bot.py
│   - Heroku           │
│   - DigitalOcean     │
└──────────────────────┘
```

## 🚀 Шаг 1: Развертывание Frontend на GitHub Pages

### 1.1. Создайте репозиторий на GitHub

```bash
# В вашем проекте
git init
git add docs/index.html
git commit -m "Add Web App frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/KuCoinBotV4.git
git push -u origin main
```

### 1.2. Настройте GitHub Pages

1. Откройте репозиторий на GitHub
2. Settings → Pages
3. Source: **Deploy from a branch**
4. Branch: **main** → Folder: **/docs**
5. Save

Ваш frontend будет доступен по адресу:
```
https://YOUR_USERNAME.github.io/KuCoinBotV4/
```

## 🖥️ Шаг 2: Развертывание Backend

### Вариант A: Railway.app (Рекомендуется, бесплатно)

1. **Создайте файл `Procfile`**:
```bash
web: uvicorn webapp.server:app --host 0.0.0.0 --port $PORT
```

2. **Создайте `railway.json`**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn webapp.server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. **Деплой на Railway**:
   - Зайдите на https://railway.app
   - Подключите GitHub репозиторий
   - Railway автоматически определит Python проект
   - Добавьте переменные окружения:
     - `KUCOIN_API_KEY`
     - `KUCOIN_API_SECRET`
     - `KUCOIN_API_PASSPHRASE`
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`

4. **Получите URL**:
   Railway выдаст URL типа: `https://your-app.railway.app`

### Вариант B: Heroku

1. **Создайте `Procfile`**:
```
web: uvicorn webapp.server:app --host 0.0.0.0 --port $PORT
worker: python main.py
```

2. **Создайте `runtime.txt`**:
```
python-3.11.0
```

3. **Деплой**:
```bash
heroku create your-bot-name
git push heroku main
heroku config:set KUCOIN_API_KEY=...
heroku config:set TELEGRAM_BOT_TOKEN=...
```

### Вариант C: DigitalOcean/VPS (Полный контроль)

```bash
# На сервере
git clone https://github.com/YOUR_USERNAME/KuCoinBotV4.git
cd KuCoinBotV4
pip install -r requirements.txt

# Создайте .env файл
nano .env

# Запустите с помощью systemd или screen
python main_with_webapp.py
```

## 🔗 Шаг 3: Соединение Frontend и Backend

### 3.1. Обновите API URL в frontend

В файле `docs/index.html` найдите строку:
```javascript
const API_URL = 'https://your-backend-server.com/api';
```

Замените на URL вашего backend:
```javascript
const API_URL = 'https://your-app.railway.app/api';
```

### 3.2. Настройте CORS в backend

В `webapp/server.py` уже настроен CORS, но убедитесь, что включен ваш GitHub Pages URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://YOUR_USERNAME.github.io",  # ← Добавьте ваш URL
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Шаг 4: Настройка в Telegram

### 4.1. Обновите WEBAPP_URL

В `.env` на backend сервере:
```env
WEBAPP_URL=https://YOUR_USERNAME.github.io/KuCoinBotV4/
```

### 4.2. Настройте кнопку в BotFather

1. Откройте [@BotFather](https://t.me/BotFather)
2. `/mybots` → Выберите бота
3. **Bot Settings** → **Menu Button**
4. **Edit Menu Button URL**
5. Введите: `https://YOUR_USERNAME.github.io/KuCoinBotV4/`
6. Название кнопки: "Открыть приложение"

## ✅ Проверка

### Frontend (GitHub Pages)
```bash
curl https://YOUR_USERNAME.github.io/KuCoinBotV4/
# Должен вернуть HTML
```

### Backend (Railway/Heroku)
```bash
curl https://your-app.railway.app/api/health
# Должен вернуть: {"status":"ok","timestamp":"...","bot_available":true}
```

### Telegram Web App
1. Откройте вашего бота в Telegram
2. Нажмите кнопку меню (или "🚀 Открыть Web App")
3. Должен открыться веб-интерфейс с данными бота

## 💰 Стоимость

| Сервис | Стоимость | Особенности |
|--------|-----------|-------------|
| **GitHub Pages** | Бесплатно | Только статика, HTTPS |
| **Railway.app** | $5/мес (500 часов бесплатно) | Простой деплой |
| **Heroku** | $7/мес | Проверенный вариант |
| **DigitalOcean** | От $4/мес | Полный контроль |

## 🐛 Troubleshooting

### Ошибка CORS
Убедитесь, что GitHub Pages URL добавлен в `allow_origins` в `server.py`

### "Bot not initialized"
Проверьте, что backend сервер запущен и бот инициализирован:
```bash
curl https://your-app.railway.app/api/health
```

### Web App не открывается
1. Проверьте, что URL в BotFather правильный
2. Убедитесь, что используется HTTPS
3. Проверьте консоль браузера (F12) на ошибки

## 📚 Дополнительно

### Автоматический деплой

GitHub Actions для автоматического обновления:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## 🎉 Готово!

Теперь ваш Web App доступен:
- **Frontend**: `https://YOUR_USERNAME.github.io/KuCoinBotV4/`
- **Backend**: `https://your-app.railway.app`
- **Telegram**: Через кнопку в боте

Полностью бесплатное решение (GitHub Pages + Railway free tier)! 🚀
