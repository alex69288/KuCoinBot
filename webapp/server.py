"""
FastAPI сервер для Telegram Web App
Предоставляет REST API для управления торговым ботом через веб-интерфейс
"""
import sys
import os
import hmac
import hashlib
import urllib.parse
from typing import Optional, Dict, Any
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils.logger import log_info, log_error

# Создаем приложение FastAPI
app = FastAPI(
    title="KuCoin Trading Bot Web App",
    description="Telegram Web App для управления торговым ботом",
    version="1.0.0"
)

# Настройка CORS для работы с Telegram Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Для Amvera и других облачных платформ
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для экземпляра бота (будет установлена при запуске)
trading_bot = None

def set_trading_bot(bot):
    """Устанавливает экземпляр торгового бота"""
    global trading_bot
    trading_bot = bot
    log_info("✅ Trading bot установлен в Web App сервере")


def _get_bot_token() -> Optional[str]:
    """Безопасно получает токен Telegram бота из экземпляра trading_bot.
    Возвращает None, если токен недоступен.
    """
    try:
        if not trading_bot:
            return None
        # Если в боте есть объект telegram с полем token
        if hasattr(trading_bot, 'telegram') and getattr(trading_bot, 'telegram'):
            token = getattr(trading_bot.telegram, 'token', None)
            if token:
                return token
        # Попробуем достать из настроек
        if hasattr(trading_bot, 'settings') and getattr(trading_bot, 'settings'):
            return trading_bot.settings.settings.get('telegram_token')
    except Exception as e:
        log_error(f"Ошибка при получении токена бота: {e}")
    return None


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    Проверяет подлинность данных от Telegram Web App
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data))
        received_hash = parsed.pop('hash', None)
        
        if not received_hash:
            return False
        
        # Создаем строку для проверки
        data_check_string = '\n'.join(
            f'{k}={v}' for k, v in sorted(parsed.items())
        )
        
        # Создаем secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        log_error(f"Ошибка проверки Telegram Web App данных: {e}")
        return False


def get_user_from_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """Извлекает данные пользователя из init_data"""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data))
        user_data = parsed.get('user', '{}')
        import json
        return json.loads(user_data)
    except Exception as e:
        log_error(f"Ошибка извлечения данных пользователя: {e}")
        return None


# Определяем директорию webapp (где находится этот файл server.py)
WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
# Директория static находится рядом с server.py
STATIC_DIR = os.path.join(WEBAPP_DIR, "static")

log_info(f"🔍 Директория webapp: {WEBAPP_DIR}")
log_info(f"🔍 Директория static: {STATIC_DIR}")
log_info(f"📂 Рабочая директория: {os.getcwd()}")

# Монтируем статические файлы ПЕРЕД маршрутами
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    log_info(f"✅ Статические файлы смонтированы из {STATIC_DIR}")
else:
    log_error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Директория static не найдена по пути {STATIC_DIR}")
    log_error(f"❌ Содержимое директории webapp: {os.listdir(WEBAPP_DIR) if os.path.exists(WEBAPP_DIR) else 'НЕ НАЙДЕНА'}")

# ============= API ENDPOINTS =============

@app.get("/ping")
async def ping():
    """Простейший тест - должен всегда работать"""
    return {"status": "pong", "message": "Server is running!"}


@app.get("/")
async def root():
    """Корневой endpoint - возвращает index.html"""
    # index.html находится в директории static рядом с server.py
    index_path = os.path.join(STATIC_DIR, 'index.html')
    
    log_info(f"🔍 GET / - Запрос главной страницы")
    log_info(f"📂 Ищем index.html по пути: {index_path}")
    
    if os.path.exists(index_path):
        log_info(f"✅ Отдаём index.html из {index_path}")
        return FileResponse(index_path)
    else:
        log_error(f"❌ index.html НЕ НАЙДЕН по пути: {index_path}")
        log_error(f"📂 Содержимое STATIC_DIR: {os.listdir(STATIC_DIR) if os.path.exists(STATIC_DIR) else 'ДИРЕКТОРИЯ НЕ СУЩЕСТВУЕТ'}")
        raise HTTPException(status_code=404, detail=f"index.html not found at {index_path}")


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "bot_available": trading_bot is not None
    }


@app.get("/api/debug/paths")
async def debug_paths():
    """Отладочный эндпоинт для проверки путей"""
    return {
        "webapp_dir": WEBAPP_DIR,
        "static_dir": STATIC_DIR,
        "cwd": os.getcwd(),
        "static_exists": os.path.exists(STATIC_DIR),
        "static_contents": os.listdir(STATIC_DIR) if os.path.exists(STATIC_DIR) else [],
        "index_exists": os.path.exists(os.path.join(STATIC_DIR, 'index.html'))
    }


@app.get("/api/status")
async def get_bot_status(init_data: str = Query(..., description="Telegram Web App init data")):
    """
    Получить текущий статус бота
    Требует валидные данные Telegram Web App
    """
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    # Проверяем подлинность данных от Telegram
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        # Получаем данные о балансе
        balance = trading_bot.exchange.get_balance()
        
        # Получаем текущую позицию
        position_info = {
            "position": trading_bot.position,
            "entry_price": trading_bot.entry_price,
            "amount": trading_bot.amount
        }
        
        # Получаем активные настройки
        settings_info = {
            "active_pair": trading_bot.settings.trading_pairs['active_pair'],
            "active_strategy": trading_bot.settings.strategy_settings['active_strategy'],
            "risk_per_trade": trading_bot.settings.risk_settings.get('risk_per_trade', 1.0),
            "max_positions": trading_bot.settings.risk_settings.get('max_positions', 3)
        }
        
        # Получаем последние метрики
        metrics = {
            "total_trades": getattr(trading_bot.metrics, 'total_trades', 0),
            "winning_trades": getattr(trading_bot.metrics, 'winning_trades', 0),
            "losing_trades": getattr(trading_bot.metrics, 'losing_trades', 0),
            "total_profit": getattr(trading_bot.metrics, 'total_profit', 0.0)
        }
        
        return {
            "is_running": trading_bot.is_running,
            "balance": balance,
            "position": position_info,
            "settings": settings_info,
            "metrics": metrics,
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        log_error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.get("/api/market")
async def get_market_data(
    init_data: str = Query(..., description="Telegram Web App init data"),
    symbol: Optional[str] = None
):
    """
    Получить данные о рынке для выбранной пары
    """
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        # Используем активную пару, если символ не указан
        if not symbol:
            symbol = trading_bot.settings.trading_pairs['active_pair']
        
        # Получаем данные о рынке
        ticker = trading_bot.exchange.fetch_ticker(symbol)
        
        return {
            "symbol": symbol,
            "current_price": ticker.get('last'),
            "high_24h": ticker.get('high'),
            "low_24h": ticker.get('low'),
            "volume_24h": ticker.get('quoteVolume'),
            "price_change_24h": ticker.get('percentage'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error(f"Ошибка получения данных рынка: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting market data: {str(e)}")


@app.post("/api/bot/start")
async def start_bot(init_data: str = Body(..., embed=True)):
    """Запустить бота"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        if not trading_bot.is_running:
            trading_bot.is_running = True
            log_info("🚀 Бот запущен через Web App")
            return {"status": "success", "message": "Бот запущен"}
        else:
            return {"status": "info", "message": "Бот уже работает"}
    except Exception as e:
        log_error(f"Ошибка запуска бота: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting bot: {str(e)}")


@app.post("/api/bot/stop")
async def stop_bot(init_data: str = Body(..., embed=True)):
    """Остановить бота"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        if trading_bot.is_running:
            trading_bot.is_running = False
            log_info("🛑 Бот остановлен через Web App")
            return {"status": "success", "message": "Бот остановлен"}
        else:
            return {"status": "info", "message": "Бот уже остановлен"}
    except Exception as e:
        log_error(f"Ошибка остановки бота: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping bot: {str(e)}")


@app.get("/api/settings")
async def get_settings(init_data: str = Query(...)):
    """Получить все настройки бота"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        return {
            "trading_pairs": trading_bot.settings.trading_pairs,
            "strategy_settings": trading_bot.settings.strategy_settings,
            "risk_settings": trading_bot.settings.risk_settings,
            "ml_settings": trading_bot.settings.ml_settings
        }
    except Exception as e:
        log_error(f"Ошибка получения настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")


class SettingsUpdate(BaseModel):
    category: str  # 'trading_pairs', 'strategy_settings', 'risk_settings', 'ml_settings'
    key: str
    value: Any


@app.post("/api/settings")
async def update_settings(
    init_data: str = Body(...),
    settings_update: SettingsUpdate = Body(...)
):
    """Обновить настройки бота"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        category = settings_update.category
        key = settings_update.key
        value = settings_update.value
        
        # Обновляем соответствующую категорию настроек
        if category == 'trading_pairs':
            trading_bot.settings.trading_pairs[key] = value
        elif category == 'strategy_settings':
            trading_bot.settings.strategy_settings[key] = value
        elif category == 'risk_settings':
            trading_bot.settings.risk_settings[key] = value
        elif category == 'ml_settings':
            trading_bot.settings.ml_settings[key] = value
        else:
            raise HTTPException(status_code=400, detail="Invalid settings category")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"⚙️ Настройки обновлены через Web App: {category}.{key} = {value}")
        
        return {
            "status": "success",
            "message": f"Настройка {key} обновлена",
            "updated_value": value
        }
    except Exception as e:
        log_error(f"Ошибка обновления настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")


@app.get("/api/trades")
async def get_trades(
    init_data: str = Query(...),
    limit: int = Query(50, ge=1, le=100)
):
    """Получить историю сделок"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        # Получаем последние сделки из метрик
        trades = []
        if hasattr(trading_bot.metrics, 'trades_history'):
            trades = trading_bot.metrics.trades_history[-limit:]
        
        return {
            "trades": trades,
            "count": len(trades)
        }
    except Exception as e:
        log_error(f"Ошибка получения истории сделок: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting trades: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    log_info("🌐 Запуск Web App сервера...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
