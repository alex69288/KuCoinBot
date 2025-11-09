"""
Тестовая версия Web App для локальной разработки
БЕЗ проверки авторизации Telegram (только для тестирования!)
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime

from utils.logger import log_info, log_error

# Создаем приложение
app = FastAPI(title="KuCoin Bot Web App - TEST MODE")

# CORS для любых источников (только для разработки!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для бота
trading_bot = None

def set_trading_bot(bot):
    global trading_bot
    trading_bot = bot
    log_info("✅ Trading bot установлен в Test Web App")


@app.get("/")
async def root():
    """Тестовая страница с демо данными"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KuCoin Bot - Test Mode</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 { margin-bottom: 15px; font-size: 20px; }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .info-row:last-child { border-bottom: none; }
        .badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            background: rgba(76, 175, 80, 0.3);
        }
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.2);
            color: white;
            transition: all 0.3s;
        }
        .btn:hover { background: rgba(255,255,255,0.3); }
        .status-running { color: #4CAF50; }
        .positive { color: #4CAF50; }
        .warning {
            background: rgba(255, 193, 7, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 KuCoin Trading Bot</h1>
            <div class="badge">🟢 TEST MODE</div>
        </div>
        
        <div class="warning">
            ⚠️ Демо режим - данные тестовые
        </div>

        <div class="card">
            <h2>📊 Статус бота</h2>
            <div class="info-row">
                <span>Состояние:</span>
                <span class="status-running">🟢 Работает</span>
            </div>
            <div class="info-row">
                <span>Позиция:</span>
                <span>LONG</span>
            </div>
        </div>

        <div class="card">
            <h2>💰 Баланс</h2>
            <div class="info-row">
                <span>USDT:</span>
                <span>1,234.56 USDT</span>
            </div>
            <div class="info-row">
                <span>Общий баланс:</span>
                <span>1,500.00 USDT</span>
            </div>
        </div>

        <div class="card">
            <h2>💹 Рынок (BTC/USDT)</h2>
            <div class="info-row">
                <span>Текущая цена:</span>
                <span>89,234.56 USDT</span>
            </div>
            <div class="info-row">
                <span>Изменение 24ч:</span>
                <span class="positive">+3.45%</span>
            </div>
        </div>

        <div class="card">
            <h2>📈 Статистика</h2>
            <div class="info-row">
                <span>Всего сделок:</span>
                <span>42</span>
            </div>
            <div class="info-row">
                <span>Прибыль:</span>
                <span class="positive">+234.56 USDT</span>
            </div>
            <div class="info-row">
                <span>Винрейт:</span>
                <span>65.5%</span>
            </div>
        </div>

        <div class="card">
            <button class="btn" onclick="alert('Функция запуска доступна в production режиме')">
                ▶️ Запустить бота
            </button>
            <button class="btn" onclick="alert('Функция остановки доступна в production режиме')">
                ⏹️ Остановить бота
            </button>
            <button class="btn" onclick="window.location.reload()">
                🔄 Обновить
            </button>
        </div>

        <div style="text-align: center; opacity: 0.7; margin-top: 20px; font-size: 12px;">
            <p>Для полной функциональности:</p>
            <p>1. Установите ngrok</p>
            <p>2. Получите HTTPS URL</p>
            <p>3. Добавьте WEBAPP_URL в .env</p>
        </div>
    </div>

    <script>
        // Инициализация Telegram Web App
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
        }
    </script>
</body>
</html>
""")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mode": "TEST",
        "timestamp": datetime.now().isoformat(),
        "bot_available": trading_bot is not None
    }


if __name__ == "__main__":
    import uvicorn
    log_info("🧪 Запуск TEST Web App сервера...")
    log_info("⚠️  ВНИМАНИЕ: Это тестовая версия без проверки авторизации!")
    log_info("🌐 Сервер доступен по адресу: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
