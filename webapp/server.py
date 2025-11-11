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
            "amount": trading_bot.current_position_size_usdt
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
        ticker = trading_bot.exchange.get_ticker(symbol)
        
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


@app.get("/api/positions")
async def get_positions(init_data: str = Query(...)):
    """Получить открытые позиции"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        positions = []
        
        # Получаем текущую позицию
        if trading_bot.position and trading_bot.position != 'none':
            ticker = trading_bot.exchange.get_ticker(
                trading_bot.settings.trading_pairs['active_pair']
            )
            current_price = ticker['last'] if ticker else 0
            
            pnl = 0
            if trading_bot.position == 'long':
                pnl = (current_price - trading_bot.entry_price) * trading_bot.current_position_size_usdt / trading_bot.entry_price
            
            positions.append({
                "id": "current_position",
                "pair": trading_bot.settings.trading_pairs['active_pair'],
                "status": trading_bot.position,
                "entry_price": trading_bot.entry_price,
                "current_price": current_price,
                "amount": trading_bot.current_position_size_usdt / trading_bot.entry_price if trading_bot.entry_price else 0,
                "pnl": pnl,
                "timestamp": datetime.now().isoformat()
            })
        
        return positions
    except Exception as e:
        log_error(f"Ошибка получения позиций: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting positions: {str(e)}")


@app.post("/api/position/{position_id}/close")
async def close_position(
    position_id: str,
    init_data: str = Body(..., embed=True)
):
    """Закрыть позицию вручную"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        if trading_bot.position and trading_bot.position != 'none':
            # Закрываем позицию
            result = trading_bot.close_position(reason="Закрыто вручную через WebApp")
            log_info(f"📴 Позиция закрыта вручную через WebApp")
            return {
                "status": "success",
                "message": "Позиция закрыта",
                "result": result
            }
        else:
            return {
                "status": "info",
                "message": "Нет открытой позиции"
            }
    except Exception as e:
        log_error(f"Ошибка закрытия позиции: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing position: {str(e)}")


@app.get("/api/analytics")
async def get_analytics(init_data: str = Query(...)):
    """Получить аналитику и статистику"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        metrics = trading_bot.metrics
        
        # Основная статистика
        total_trades = getattr(metrics, 'total_trades', 0)
        winning_trades = getattr(metrics, 'winning_trades', 0)
        losing_trades = getattr(metrics, 'losing_trades', 0)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Прибыли/убытки
        total_profit = getattr(metrics, 'total_profit', 0.0)
        avg_profit = (total_profit / total_trades) if total_trades > 0 else 0
        
        # Максимальные значения
        max_win = getattr(metrics, 'max_win', 0.0)
        max_loss = getattr(metrics, 'max_loss', 0.0)
        
        # Средние значения для прибыльных и убыточных сделок
        avg_win = 0
        avg_loss = 0
        
        if hasattr(metrics, 'trades_history') and metrics.trades_history:
            profitable_trades = [t for t in metrics.trades_history if t.get('pnl', 0) > 0]
            losing_trades_list = [t for t in metrics.trades_history if t.get('pnl', 0) < 0]
            
            if profitable_trades:
                avg_win = sum(t['pnl'] for t in profitable_trades) / len(profitable_trades)
            if losing_trades_list:
                avg_loss = sum(t['pnl'] for t in losing_trades_list) / len(losing_trades_list)
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "avg_profit": round(avg_profit, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_win": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_error(f"Ошибка получения аналитики: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")


@app.post("/api/analytics/reset")
async def reset_analytics(init_data: str = Body(..., embed=True)):
    """Сбросить статистику"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        # Сбрасываем метрики
        if hasattr(trading_bot.metrics, 'reset'):
            trading_bot.metrics.reset()
        else:
            trading_bot.metrics.total_trades = 0
            trading_bot.metrics.winning_trades = 0
            trading_bot.metrics.losing_trades = 0
            trading_bot.metrics.total_profit = 0.0
            trading_bot.metrics.max_win = 0.0
            trading_bot.metrics.max_loss = 0.0
            if hasattr(trading_bot.metrics, 'trades_history'):
                trading_bot.metrics.trades_history = []
        
        log_info("🗑️ Статистика сброшена через WebApp")
        
        return {
            "status": "success",
            "message": "Статистика сброшена"
        }
    except Exception as e:
        log_error(f"Ошибка сброса статистики: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting analytics: {str(e)}")


class TradingSettingsUpdate(BaseModel):
    active_pair: Optional[str] = None
    active_strategy: Optional[str] = None
    trade_amount_percent: Optional[float] = None


@app.post("/api/settings/trading")
async def update_trading_settings(
    init_data: str = Body(...),
    settings: TradingSettingsUpdate = Body(...)
):
    """Обновить торговые настройки"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        updated = []
        
        if settings.active_pair is not None:
            trading_bot.settings.trading_pairs['active_pair'] = settings.active_pair
            updated.append(f"Пара: {settings.active_pair}")
        
        if settings.active_strategy is not None:
            trading_bot.settings.strategy_settings['active_strategy'] = settings.active_strategy
            updated.append(f"Стратегия: {settings.active_strategy}")
        
        if settings.trade_amount_percent is not None:
            trading_bot.settings.settings['trade_amount_percent'] = settings.trade_amount_percent
            updated.append(f"Размер позиции: {settings.trade_amount_percent}%")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"⚙️ Торговые настройки обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "Торговые настройки обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления торговых настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating trading settings: {str(e)}")


class EmaSettingsUpdate(BaseModel):
    ema_fast_period: Optional[int] = None
    ema_slow_period: Optional[int] = None
    ema_threshold: Optional[float] = None


@app.post("/api/settings/ema")
async def update_ema_settings(
    init_data: str = Body(...),
    settings: EmaSettingsUpdate = Body(...)
):
    """Обновить настройки EMA"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        strategy = trading_bot.get_active_strategy()
        updated = []
        
        if settings.ema_fast_period is not None:
            strategy.settings['ema_fast_period'] = settings.ema_fast_period
            updated.append(f"Быстрая EMA: {settings.ema_fast_period}")
        
        if settings.ema_slow_period is not None:
            strategy.settings['ema_slow_period'] = settings.ema_slow_period
            updated.append(f"Медленная EMA: {settings.ema_slow_period}")
        
        if settings.ema_threshold is not None:
            strategy.settings['ema_threshold'] = settings.ema_threshold
            updated.append(f"Порог EMA: {settings.ema_threshold}%")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"📈 EMA настройки обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "EMA настройки обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления EMA настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating EMA settings: {str(e)}")


class RiskSettingsUpdate(BaseModel):
    take_profit_percent: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    max_position_size: Optional[float] = None
    max_daily_loss: Optional[float] = None


@app.post("/api/settings/risk")
async def update_risk_settings(
    init_data: str = Body(...),
    settings: RiskSettingsUpdate = Body(...)
):
    """Обновить настройки риск-менеджмента"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        strategy = trading_bot.get_active_strategy()
        updated = []
        
        if settings.take_profit_percent is not None:
            strategy.settings['take_profit_percent'] = settings.take_profit_percent
            updated.append(f"Take Profit: {settings.take_profit_percent}%")
        
        if settings.stop_loss_percent is not None:
            strategy.settings['stop_loss_percent'] = settings.stop_loss_percent
            updated.append(f"Stop Loss: {settings.stop_loss_percent}%")
        
        if settings.max_position_size is not None:
            trading_bot.settings.risk_settings['max_position_size'] = settings.max_position_size
            updated.append(f"Макс. позиция: {settings.max_position_size} USDT")
        
        if settings.max_daily_loss is not None:
            trading_bot.settings.risk_settings['max_daily_loss'] = settings.max_daily_loss
            updated.append(f"Макс. убыток/день: {settings.max_daily_loss} USDT")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"🛡️ Риск настройки обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "Риск настройки обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления риск настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating risk settings: {str(e)}")


class MLSettingsUpdate(BaseModel):
    ml_enabled: Optional[bool] = None
    ml_buy_threshold: Optional[float] = None
    ml_sell_threshold: Optional[float] = None


@app.post("/api/settings/ml")
async def update_ml_settings(
    init_data: str = Body(...),
    settings: MLSettingsUpdate = Body(...)
):
    """Обновить ML настройки"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        strategy = trading_bot.get_active_strategy()
        updated = []
        
        if settings.ml_enabled is not None:
            strategy.settings['ml_enabled'] = settings.ml_enabled
            updated.append(f"ML: {'включен' if settings.ml_enabled else 'выключен'}")
        
        if settings.ml_buy_threshold is not None:
            strategy.settings['ml_buy_threshold'] = settings.ml_buy_threshold
            updated.append(f"Порог покупки: {settings.ml_buy_threshold}")
        
        if settings.ml_sell_threshold is not None:
            strategy.settings['ml_sell_threshold'] = settings.ml_sell_threshold
            updated.append(f"Порог продажи: {settings.ml_sell_threshold}")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"🤖 ML настройки обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "ML настройки обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления ML настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating ML settings: {str(e)}")


@app.post("/api/ml/retrain")
async def retrain_ml_model(init_data: str = Body(..., embed=True)):
    """Переобучить ML модель"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        strategy = trading_bot.get_active_strategy()
        
        # Проверяем, есть ли у стратегии ML модель
        if hasattr(strategy, 'ml_model') and hasattr(strategy.ml_model, 'train'):
            strategy.ml_model.train()
            log_info("🤖 ML модель переобучена через WebApp")
            return {
                "status": "success",
                "message": "ML модель успешно переобучена"
            }
        else:
            return {
                "status": "info",
                "message": "ML модель недоступна для текущей стратегии"
            }
    except Exception as e:
        log_error(f"Ошибка переобучения ML модели: {e}")
        raise HTTPException(status_code=500, detail=f"Error retraining ML model: {str(e)}")


class GeneralSettingsUpdate(BaseModel):
    trading_enabled: Optional[bool] = None
    demo_mode: Optional[bool] = None
    enable_price_updates: Optional[bool] = None
    trailing_stop: Optional[bool] = None


@app.post("/api/settings/general")
async def update_general_settings(
    init_data: str = Body(...),
    settings: GeneralSettingsUpdate = Body(...)
):
    """Обновить общие настройки"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        updated = []
        
        if settings.trading_enabled is not None:
            trading_bot.settings.settings['trading_enabled'] = settings.trading_enabled
            updated.append(f"Торговля: {'включена' if settings.trading_enabled else 'выключена'}")
        
        if settings.demo_mode is not None:
            trading_bot.settings.settings['demo_mode'] = settings.demo_mode
            updated.append(f"Демо режим: {'включен' if settings.demo_mode else 'выключен'}")
        
        if settings.enable_price_updates is not None:
            trading_bot.settings.settings['enable_price_updates'] = settings.enable_price_updates
            updated.append(f"Обновления цены: {'включены' if settings.enable_price_updates else 'выключены'}")
        
        if settings.trailing_stop is not None:
            strategy = trading_bot.get_active_strategy()
            strategy.settings['trailing_stop'] = settings.trailing_stop
            updated.append(f"Trailing Stop: {'включен' if settings.trailing_stop else 'выключен'}")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"🔧 Общие настройки обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "Общие настройки обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления общих настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating general settings: {str(e)}")


@app.get("/api/trade-history")
async def get_trade_history(
    init_data: str = Query(...),
    limit: int = Query(10, ge=1, le=50)
):
    """Получить историю сделок (упрощенная версия)"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        history = []
        
        if hasattr(trading_bot.metrics, 'trades_history'):
            history = trading_bot.metrics.trades_history[-limit:]
        
        return history
    except Exception as e:
        log_error(f"Ошибка получения истории сделок: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting trade history: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    log_info("🌐 Запуск Web App сервера...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
