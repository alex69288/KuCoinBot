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

# 🔧 Конфигурация asyncio для корректной работы на Windows (перед импортом FastAPI)
from utils.asyncio_config import configure_asyncio, suppress_asyncio_debug_warnings
configure_asyncio()
suppress_asyncio_debug_warnings()

from fastapi import FastAPI, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import json

from utils.logger import log_info, log_error

# Импортируем компактные форматы для оптимизации трафика
try:
    from webapp.api_compact_responses import (
        compact_status_response,
        compact_market_response,
        compact_positions_response,
        compact_history_response,
        compact_settings_response,
        compact_analytics_response
    )
    log_info("[OK] Компактные форматы API загружены для оптимизации трафика v0.1.9")
except ImportError:
    log_info("[WARN] Компактные форматы API не доступны, используются полные ответы")
    compact_status_response = None

# Создаем приложение FastAPI
app = FastAPI(
    title="KuCoin Trading Bot Web App",
    description="Telegram Web App для управления торговым ботом",
    version="1.0.0"
)

# Добавляем сжатие GZip для уменьшения размера передаваемых данных
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Сжимаем ответы больше 1KB

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
    log_info("[OK] Trading bot установлен в Web App сервере")


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
    
    В режиме разработки (DEV_MODE=1) пропускает проверку для локального тестирования
    """
    # 🔧 Режим разработки - пропускаем аутентификацию
    dev_mode = os.getenv('DEV_MODE', '0') == '1'
    if dev_mode:
        log_info("[DEV] Пропуск аутентификации в режиме разработки")
        return True
    
    # Пустой init_data - пропускаем в DEV режиме
    if not init_data or init_data == 'debug_mode':
        if dev_mode:
            return True
        log_error("[AUTH] Пустой init_data в production режиме")
        return False
    
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
# Корневая директория проекта (один уровень выше webapp)
PROJECT_ROOT = os.path.dirname(WEBAPP_DIR)
# Директория static находится рядом с server.py
STATIC_DIR = os.path.join(WEBAPP_DIR, "static")

log_info(f"[INFO] Корневая директория проекта: {PROJECT_ROOT}")
log_info(f"[INFO] Директория webapp: {WEBAPP_DIR}")
log_info(f"[INFO] Директория static: {STATIC_DIR}")
log_info(f"[DIR] Рабочая директория: {os.getcwd()}")

# Создаем класс для кэширования статических файлов
class CachedStaticFiles(StaticFiles):
    """StaticFiles с поддержкой кэширования для оптимизации загрузки"""
    
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        
        # Добавляем заголовки кэширования для статических ресурсов
        if path.endswith(('.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2')):
            # Кэшируем на 1 день
            response.headers['Cache-Control'] = 'public, max-age=86400, immutable'
        elif path.endswith('.html'):
            # HTML кэшируем минимально (5 минут) для получения обновлений
            response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'
        
        # Добавляем сжатие
        response.headers['Vary'] = 'Accept-Encoding'
        
        return response

# Монтируем статические файлы ПЕРЕД маршрутами с оптимизацией кэширования
if os.path.exists(STATIC_DIR):
    app.mount("/static", CachedStaticFiles(directory=STATIC_DIR), name="static")
    log_info(f"[OK] Статические файлы смонтированы из {STATIC_DIR} с кэшированием")
else:
    log_error(f"[ERROR] КРИТИЧЕСКАЯ ОШИБКА: Директория static не найдена по пути {STATIC_DIR}")
    log_error(f"[ERROR] Содержимое директории webapp: {os.listdir(WEBAPP_DIR) if os.path.exists(WEBAPP_DIR) else 'НЕ НАЙДЕНА'}")

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
    
    log_info(f"[INFO] GET / - Запрос главной страницы")
    log_info(f"[DIR] Ищем index.html по пути: {index_path}")
    
    if os.path.exists(index_path):
        log_info(f"[OK] Отдаём index.html из {index_path}")
        return FileResponse(index_path)
    else:
        log_error(f"[ERROR] index.html НЕ НАЙДЕН по пути: {index_path}")
        log_error(f"[DIR] Содержимое STATIC_DIR: {os.listdir(STATIC_DIR) if os.path.exists(STATIC_DIR) else 'ДИРЕКТОРИЯ НЕ СУЩЕСТВУЕТ'}")
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
async def get_bot_status(
    init_data: str = Query(..., description="Telegram Web App init data"),
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
):
    """
    Получить текущий статус бота
    Требует валидные данные Telegram Web App
    
    Параметры:
    - init_data: Данные из Telegram Web App
    - compact: 1 для компактного формата (-60-70% трафика)
    """
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    # Проверяем подлинность данных от Telegram
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        import os
        from utils.position_manager import load_position_state
        
        # Получаем текущую цену
        current_price = 0
        try:
            ticker = trading_bot.exchange.get_ticker(trading_bot.settings.trading_pairs['active_pair'])
            current_price = ticker.get('last', 0) if ticker else 0
        except:
            pass
        
        # Получаем информацию о позициях
        positions_info = {
            "open_count": 0,
            "size_usdt": 0,
            "entry_price": 0,
            "current_profit_percent": 0,
            "current_profit_usdt": 0,
            "to_take_profit": 0,
            "tp_target": trading_bot.settings.risk_settings.get('take_profit_percent', 2.0),
            "fee_percent": 0.2,
            "fee_usdt": 0
        }
        
        # 🔧 ПОДСЧЕТ ИЗ ФАЙЛА СОСТОЯНИЯ
        total_open_positions = 0
        total_position_size_usdt = 0
        total_pnl_usdt = 0
        total_pnl_percent = 0
        
        # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
        position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
        if os.path.exists(position_state_path):
            state = load_position_state(position_state_path)
            
            # Считаем общее количество открытых позиций по всем парам
            for pair_symbol, pair_data in state.items():
                if isinstance(pair_data, dict) and 'positions' in pair_data:
                    positions_list = pair_data.get('positions', [])
                    total_open_positions += len(positions_list)
                    total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
                    
                    # Рассчитываем общий PnL
                    for pos in positions_list:
                        try:
                            ticker = trading_bot.exchange.get_ticker(pair_symbol)
                            current_price_pair = ticker.get('last', 0) if ticker else 0
                            
                            entry_price = pos.get('entry_price', 0)
                            position_size_usdt = pos.get('position_size_usdt', 0)
                            
                            if entry_price > 0 and current_price_pair > 0:
                                pnl = (current_price_pair - entry_price) * position_size_usdt / entry_price
                                total_pnl_usdt += pnl
                        except:
                            pass
        
        positions_info["open_count"] = total_open_positions
        positions_info["size_usdt"] = total_position_size_usdt
        
        # Рассчитываем среднюю прибыль
        if total_position_size_usdt > 0 and total_pnl_usdt != 0:
            positions_info["current_profit_percent"] = (total_pnl_usdt / total_position_size_usdt) * 100
            positions_info["current_profit_usdt"] = total_pnl_usdt
            positions_info["to_take_profit"] = positions_info["tp_target"] - positions_info["current_profit_percent"]
            positions_info["fee_usdt"] = total_position_size_usdt * 0.004
        
        # Для совместимости - если нет файла состояния, используем старый способ
        if total_open_positions == 0 and trading_bot.position and trading_bot.position == 'long' and trading_bot.entry_price:
            positions_info["open_count"] = 1
            positions_info["size_usdt"] = trading_bot.current_position_size_usdt or 0
            positions_info["entry_price"] = trading_bot.entry_price
            
            # Рассчитываем текущую прибыль
            if current_price and trading_bot.position == 'long':
                profit_percent = ((current_price - trading_bot.entry_price) / trading_bot.entry_price) * 100
                profit_usdt = profit_percent / 100 * positions_info["size_usdt"]
                positions_info["current_profit_percent"] = profit_percent
                positions_info["current_profit_usdt"] = profit_usdt
                
                # Рассчитываем до Take Profit
                tp_target = positions_info["tp_target"]
                positions_info["to_take_profit"] = tp_target - profit_percent
                
                # Комиссии (0.2% на вход + 0.2% на выход)
                positions_info["fee_usdt"] = positions_info["size_usdt"] * 0.004
        
        # Формируем ответ в формате, ожидаемом frontend
        full_response = {
            "positions": positions_info,
            "last_update": datetime.now().isoformat()
        }
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact and compact_status_response:
            return compact_status_response(full_response)
        
        return full_response
    except Exception as e:
        log_error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.get("/api/market")
async def get_market_data(
    init_data: str = Query(..., description="Telegram Web App init data"),
    symbol: Optional[str] = None,
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
):
    """
    Получить данные о рынке для выбранной пары
    
    Параметры:
    - init_data: Данные из Telegram Web App
    - symbol: Символ торговой пары (если не указан, используется активная пара)
    - compact: 1 для компактного формата (-60-70% трафика)
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
        
        # Получаем данные о рынке через метод get_ticker из exchange.py
        ticker = trading_bot.exchange.get_ticker(symbol)
        
        if not ticker:
            raise HTTPException(status_code=500, detail="Failed to fetch ticker data")
        
        # Получаем данные EMA
        ema_info = {
            "signal": "wait",
            "text": "BBEPX",
            "percent": 0
        }

        try:
            latest_market = getattr(trading_bot, 'latest_market_data', None)
            strategy = getattr(trading_bot, 'strategy', None)

            ema_fast = None
            ema_slow = None
            ema_diff = None

            if latest_market:
                ema_fast = latest_market.get('fast_ema')
                ema_slow = latest_market.get('slow_ema')
                ema_diff = latest_market.get('ema_diff_percent')
                if ema_diff is not None:
                    ema_diff *= 100

            # Если данных из последнего цикла нет, пробуем взять из стратегии
            if ema_fast is None and strategy and hasattr(strategy, 'ema_fast'):
                ema_fast = getattr(strategy, 'ema_fast', None)
            if ema_slow is None and strategy and hasattr(strategy, 'ema_slow'):
                ema_slow = getattr(strategy, 'ema_slow', None)
            if ema_diff is None and strategy and hasattr(strategy, 'ema_diff_percent'):
                ema_diff = getattr(strategy, 'ema_diff_percent', None)
                if ema_diff is not None:
                    ema_diff *= 100

            if ema_fast and ema_slow and ema_diff is not None:
                ema_info["percent"] = ema_diff

                threshold = None
                if strategy and hasattr(strategy, 'settings'):
                    threshold = strategy.settings.get('ema_threshold')
                if threshold is None:
                    threshold = trading_bot.settings.strategy_settings.get('ema_threshold')
                if threshold is None:
                    threshold = trading_bot.settings.settings.get('ema_cross_threshold', 0.005)
                if threshold > 1:
                    threshold = threshold / 100
                threshold_percent = threshold * 100

                if ema_diff > threshold_percent:
                    ema_info["signal"] = "buy"
                    ema_info["text"] = "BBEPX"
                elif ema_diff < -threshold_percent:
                    ema_info["signal"] = "sell"
                    ema_info["text"] = "НИЖЕ"
                else:
                    ema_info["signal"] = "wait"
                    ema_info["text"] = "НЕЙТРАЛЬНО"
        except Exception as e:
            log_error(f"Ошибка получения EMA: {e}")
        
        # Получаем сигнал от стратегии
        signal = "wait"
        try:
            if hasattr(trading_bot, 'last_signal'):
                signal = trading_bot.last_signal or "wait"
        except:
            pass
        
        # Получаем прогноз ML
        ml_info = {
            "prediction": 0.5,
            "confidence": 0
        }
        
        try:
            if hasattr(trading_bot, 'ml_model') and trading_bot.ml_model:
                # Получаем последний прогноз
                if hasattr(trading_bot, 'last_ml_prediction'):
                    ml_info["prediction"] = trading_bot.last_ml_prediction or 0.5
                    ml_info["confidence"] = abs(ml_info["prediction"] - 0.5) * 2
        except Exception as e:
            log_error(f"Ошибка получения ML прогноза: {e}")
        
        # Получаем изменение за 24 часа (биржа возвращает его в процентах)
        change_24h = ticker.get('change', 0)
        
        # 🔍 DEBUG: Логируем значение для отладки
        if change_24h == 0:
            log_info(f"⚠️ change_24h = 0 для {symbol}. Ticker data: {ticker}")
        else:
            log_info(f"✅ change_24h = {change_24h}% для {symbol} (из /api/market)")
        
        # Формируем ответ в формате, ожидаемом frontend
        full_response = {
            "symbol": symbol,
            "current_price": ticker.get('last', 0),
            "high_24h": ticker.get('high', 0),
            "low_24h": ticker.get('low', 0),
            "volume_24h": ticker.get('volume', 0),
            "change_24h": change_24h,  # Реальное изменение за 24 часа с биржи
            "ema": ema_info,
            "signal": signal,
            "ml": ml_info,
            "timestamp": datetime.now().isoformat()
        }
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact and compact_market_response:
            return compact_market_response(full_response)
        
        return full_response
    except HTTPException:
        raise
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
            log_info("[START] Бот запущен через Web App")
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
            log_info("[STOP] Бот остановлен через Web App")
            return {"status": "success", "message": "Бот остановлен"}
        else:
            return {"status": "info", "message": "Бот уже остановлен"}
    except Exception as e:
        log_error(f"Ошибка остановки бота: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping bot: {str(e)}")


@app.get("/api/settings")
async def get_settings(
    init_data: str = Query(...),
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
):
    """Получить все настройки бота"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        full_response = {
            "trading_pairs": trading_bot.settings.trading_pairs,
            "strategy_settings": trading_bot.settings.strategy_settings,
            "risk_settings": trading_bot.settings.risk_settings,
            "ml_settings": trading_bot.settings.ml_settings
        }
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact and compact_settings_response:
            return compact_settings_response(full_response)
        
        return full_response
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
        
        log_info(f"[CONFIG] Настройки обновлены через Web App: {category}.{key} = {value}")
        
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
async def get_positions(
    init_data: str = Query(...),
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
):
    """Получить все открытые позиции из файла состояния"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        import os
        import json
        from utils.position_manager import load_position_state
        
        positions = []
        
        # Загружаем ВСЕ позиции из файла состояния
        # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
        position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
        if os.path.exists(position_state_path):
            state = load_position_state(position_state_path)
            
            # Проходим по всем парам
            for pair_symbol, pair_data in state.items():
                if isinstance(pair_data, dict) and 'positions' in pair_data:
                    # Проходим по всем открытым позициям в паре
                    for pos_data in pair_data.get('positions', []):
                        try:
                            ticker = trading_bot.exchange.get_ticker(pair_symbol)
                            current_price = ticker['last'] if ticker else 0
                            
                            entry_price = pos_data.get('entry_price', 0)
                            position_size_usdt = pos_data.get('position_size_usdt', 0)
                            
                            # Вычисляем PnL
                            pnl = 0
                            if entry_price > 0 and current_price > 0:
                                pnl = (current_price - entry_price) * position_size_usdt / entry_price
                            
                            positions.append({
                                "id": f"{pair_symbol}_{pos_data.get('id', 0)}",
                                "pair": pair_symbol,
                                "status": "long",
                                "entry_price": entry_price,
                                "current_price": current_price,
                                "amount": pos_data.get('amount_crypto', 0),
                                "position_size_usdt": position_size_usdt,
                                "pnl": pnl,
                                "pnl_percent": ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0,
                                "opened_at": pos_data.get('opened_at', 0),
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as e:
                            log_error(f"Ошибка обработки позиции {pos_data.get('id')}: {e}")
                            continue
        
        # Если файл позиций не найден, возвращаем текущую позицию для обратной совместимости
        if not positions and trading_bot.position and trading_bot.position != 'none':
            try:
                ticker = trading_bot.exchange.get_ticker(
                    trading_bot.settings.trading_pairs['active_pair']
                )
                current_price = ticker['last'] if ticker else 0
                
                pnl = 0
                if trading_bot.position == 'long' and trading_bot.entry_price > 0:
                    pnl = (current_price - trading_bot.entry_price) * trading_bot.current_position_size_usdt / trading_bot.entry_price
                
                positions.append({
                    "id": "current_position",
                    "pair": trading_bot.settings.trading_pairs['active_pair'],
                    "status": trading_bot.position,
                    "entry_price": trading_bot.entry_price,
                    "current_price": current_price,
                    "amount": trading_bot.current_position_size_usdt / trading_bot.entry_price if trading_bot.entry_price else 0,
                    "position_size_usdt": trading_bot.current_position_size_usdt,
                    "pnl": pnl,
                    "pnl_percent": ((current_price - trading_bot.entry_price) / trading_bot.entry_price * 100) if trading_bot.entry_price > 0 else 0,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                log_error(f"Ошибка получения текущей позиции: {e}")
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact:
            # Возвращаем просто список позиций в компактном формате
            # (фронтенд обрабатывает это)
            return {
                'positions': positions,
                'count': len(positions),
                'timestamp': datetime.now().isoformat()
            }
        
        # Возвращаем полный формат (фронтенд ожидает это)
        return positions
    except Exception as e:
        log_error(f"Ошибка получения позиций: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting positions: {str(e)}")


@app.post("/api/positions/{position_id}/close")
async def close_position(
    position_id: str,
    init_data: str = Body(..., embed=True)
):
    """Закрыть конкретную позицию вручную"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        import os
        import json
        from utils.position_manager import load_position_state
        
        # Парсим ID позиции (формат: "PAIR_ID")
        parts = position_id.split('_')
        if len(parts) < 2:
            return {
                "status": "error",
                "message": "Неверный формат ID позиции"
            }
        
        pair_symbol = '_'.join(parts[:-1])  # Все кроме последней части
        pos_id = parts[-1]  # Последняя часть - ID позиции
        
        # Загружаем состояние
        # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
        position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
        if os.path.exists(position_state_path):
            state = load_position_state(position_state_path)
            
            if pair_symbol in state and 'positions' in state[pair_symbol]:
                pair_data = state[pair_symbol]
                
                # Находим позицию по ID
                pos_index = None
                for idx, pos in enumerate(pair_data['positions']):
                    if str(pos.get('id')) == pos_id:
                        pos_index = idx
                        break
                
                if pos_index is not None:
                    position = pair_data['positions'][pos_index]
                    amount = position.get('amount_crypto', 0)
                    
                    # Пытаемся продать
                    try:
                        result = trading_bot.exchange.sell(pair_symbol, amount)
                        log_info(f"[CLOSE] Позиция {pair_symbol}#{pos_id} закрыта вручную через WebApp. Результат: {result}")
                        
                        # Удаляем позицию из списка
                        pair_data['positions'].pop(pos_index)
                        pair_data['next_position_id'] = max(p['id'] for p in pair_data['positions']) + 1 if pair_data['positions'] else 1
                        
                        # Пересчитываем итоги
                        pair_data['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in pair_data['positions'])
                        pair_data['total_amount_crypto'] = sum(p['amount_crypto'] for p in pair_data['positions'])
                        
                        if pair_data['positions']:
                            total_cost = pair_data['total_position_size_usdt']
                            total_amount = pair_data['total_amount_crypto']
                            pair_data['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
                            pair_data['max_entry_price'] = max(p['entry_price'] for p in pair_data['positions'])
                        else:
                            pair_data['average_entry_price'] = 0
                            pair_data['max_entry_price'] = 0
                        
                        # Сохраняем обновленное состояние
                        # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
                        position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
                        with open(position_state_path, 'w') as f:
                            json.dump(state, f, indent=2)
                        
                        return {
                            "status": "success",
                            "message": f"Позиция {pair_symbol}#{pos_id} закрыта",
                            "result": result
                        }
                    except Exception as e:
                        log_error(f"Ошибка при продаже позиции: {e}")
                        return {
                            "status": "error",
                            "message": f"Ошибка при закрытии позиции: {str(e)}"
                        }
                else:
                    return {
                        "status": "error",
                        "message": f"Позиция {position_id} не найдена"
                    }
        
        # Fallback - закрываем текущую позицию если она есть
        if trading_bot.position and trading_bot.position != 'none':
            result = trading_bot.close_position(reason="Закрыто вручную через WebApp")
            log_info(f"[CLOSE] Текущая позиция закрыта вручную через WebApp")
            return {
                "status": "success",
                "message": "Позиция закрыта",
                "result": result
            }
        else:
            return {
                "status": "info",
                "message": "Позиция не найдена"
            }
    except Exception as e:
        log_error(f"Ошибка закрытия позиции: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing position: {str(e)}")


@app.post("/api/positions/close-all")
async def close_all_positions(init_data: str = Body(..., embed=True)):
    """Закрыть все открытые позиции"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        import os
        import json
        from utils.position_manager import load_position_state
        
        closed_count = 0
        errors = []
        
        # Загружаем состояние
        # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
        position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
        if os.path.exists(position_state_path):
            state = load_position_state(position_state_path)
            
            # Проходим по всем парам
            for pair_symbol, pair_data in list(state.items()):
                if isinstance(pair_data, dict) and 'positions' in pair_data:
                    # Проходим по всем позициям (в обратном порядке, чтобы удаление не сбивало индексы)
                    for pos in pair_data['positions'][::-1]:
                        try:
                            amount = pos.get('amount_crypto', 0)
                            if amount > 0:
                                # Пытаемся продать
                                result = trading_bot.exchange.sell(pair_symbol, amount)
                                closed_count += 1
                                log_info(f"[CLOSE-ALL] Позиция {pair_symbol}#{pos.get('id')} закрыта. Результат: {result}")
                                
                                # Удаляем позицию
                                pair_data['positions'].remove(pos)
                        except Exception as e:
                            log_error(f"Ошибка закрытия позиции {pair_symbol}#{pos.get('id')}: {e}")
                            errors.append(f"{pair_symbol}#{pos.get('id')}: {str(e)}")
                    
                    # Пересчитываем итоги для пары
                    pair_data['next_position_id'] = max(p['id'] for p in pair_data['positions']) + 1 if pair_data['positions'] else 1
                    pair_data['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in pair_data['positions'])
                    pair_data['total_amount_crypto'] = sum(p['amount_crypto'] for p in pair_data['positions'])
                    
                    if pair_data['positions']:
                        total_cost = pair_data['total_position_size_usdt']
                        total_amount = pair_data['total_amount_crypto']
                        pair_data['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
                        pair_data['max_entry_price'] = max(p['entry_price'] for p in pair_data['positions'])
                    else:
                        pair_data['average_entry_price'] = 0
                        pair_data['max_entry_price'] = 0
            
            # Сохраняем обновленное состояние
            # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
            position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
            with open(position_state_path, 'w') as f:
                json.dump(state, f, indent=2)
        
        log_info(f"[CLOSE-ALL] Все позиции закрыты вручную через WebApp (закрыто: {closed_count})")
        
        return {
            "status": "success" if not errors else "partial",
            "message": f"Закрыто позиций: {closed_count}",
            "closed_count": closed_count,
            "errors": errors if errors else None
        }
    except Exception as e:
        log_error(f"Ошибка закрытия всех позиций: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing all positions: {str(e)}")


@app.get("/api/analytics")
async def get_analytics(
    init_data: str = Query(...),
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
):
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
        
        # Статистика за сегодня
        today_stats = {"trades": 0, "pnl": 0, "win_rate": 0, "best_trade": 0}
        
        if hasattr(metrics, 'trades_history') and metrics.trades_history:
            from datetime import date
            today = date.today()
            today_trades = [
                t for t in metrics.trades_history 
                if 'timestamp' in t and t['timestamp'].startswith(today.isoformat())
            ]
            
            if today_trades:
                today_stats["trades"] = len(today_trades)
                today_stats["pnl"] = sum(t.get('pnl', 0) for t in today_trades)
                today_winning = len([t for t in today_trades if t.get('pnl', 0) > 0])
                today_stats["win_rate"] = (today_winning / len(today_trades) * 100) if today_trades else 0
                today_pnls = [t.get('pnl', 0) for t in today_trades]
                today_stats["best_trade"] = max(today_pnls) if today_pnls else 0
        
        full_response = {
            "total_trades": total_trades,
            "profitable_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_profit, 2),
            "avg_profit": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_profit": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            "today": {
                "trades": today_stats["trades"],
                "pnl": round(today_stats["pnl"], 2),
                "win_rate": round(today_stats["win_rate"], 2),
                "best_trade": round(today_stats["best_trade"], 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact and compact_analytics_response:
            return compact_analytics_response(full_response)
        
        return full_response
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
        
        log_info("[DELETE] Статистика сброшена через WebApp")
        
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
        
        log_info(f"[CONFIG] Торговые настройки обновлены через WebApp: {', '.join(updated)}")
        
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
        
        log_info(f"[ANALYSIS] EMA настройки обновлены через WebApp: {', '.join(updated)}")
        
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
        
        log_info(f"[RISK] Риск настройки обновлены через WebApp: {', '.join(updated)}")
        
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
        
        log_info(f"[ML] ML настройки обновлены через WebApp: {', '.join(updated)}")
        
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
            log_info("[ML] ML модель переобучена через WebApp")
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


class NotificationSettingsUpdate(BaseModel):
    """Модель для обновления настроек уведомлений"""
    notify_trades: Optional[bool] = None
    notify_tp_approach: Optional[bool] = None
    tp_approach_threshold: Optional[float] = None
    notify_stop_loss: Optional[bool] = None
    notify_price_changes: Optional[bool] = None
    price_change_threshold: Optional[float] = None
    notify_signals: Optional[bool] = None


@app.post("/api/settings/notifications")
async def update_notification_settings(
    init_data: str = Body(...),
    settings: NotificationSettingsUpdate = Body(...)
):
    """Обновить настройки уведомлений"""
    if not trading_bot:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    bot_token = _get_bot_token()
    if not bot_token or not verify_telegram_webapp_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram data")
    
    try:
        # Создаем раздел для настроек уведомлений, если его нет
        if 'notification_settings' not in trading_bot.settings.settings:
            trading_bot.settings.settings['notification_settings'] = {}
        
        notifications = trading_bot.settings.settings['notification_settings']
        updated = []
        
        if settings.notify_trades is not None:
            notifications['notify_trades'] = settings.notify_trades
            updated.append(f"Уведомления о сделках: {'включены' if settings.notify_trades else 'выключены'}")
        
        if settings.notify_tp_approach is not None:
            notifications['notify_tp_approach'] = settings.notify_tp_approach
            updated.append(f"Уведомления о TP: {'включены' if settings.notify_tp_approach else 'выключены'}")
        
        if settings.tp_approach_threshold is not None:
            notifications['tp_approach_threshold'] = settings.tp_approach_threshold
            updated.append(f"Порог TP: {settings.tp_approach_threshold}%")
        
        if settings.notify_stop_loss is not None:
            notifications['notify_stop_loss'] = settings.notify_stop_loss
            updated.append(f"Уведомления о SL: {'включены' if settings.notify_stop_loss else 'выключены'}")
        
        if settings.notify_price_changes is not None:
            notifications['notify_price_changes'] = settings.notify_price_changes
            updated.append(f"Уведомления о цене: {'включены' if settings.notify_price_changes else 'выключены'}")
        
        if settings.price_change_threshold is not None:
            notifications['price_change_threshold'] = settings.price_change_threshold
            updated.append(f"Порог цены: {settings.price_change_threshold}%")
        
        if settings.notify_signals is not None:
            notifications['notify_signals'] = settings.notify_signals
            updated.append(f"Уведомления о сигналах: {'включены' if settings.notify_signals else 'выключены'}")
        
        # Сохраняем настройки
        trading_bot.settings.save_settings()
        
        log_info(f"🔔 Настройки уведомлений обновлены через WebApp: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "Настройки уведомлений обновлены",
            "updated": updated
        }
    except Exception as e:
        log_error(f"Ошибка обновления настроек уведомлений: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating notification settings: {str(e)}")


@app.get("/api/trade-history")
async def get_trade_history(
    init_data: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    compact: int = Query(0, description="Компактный формат ответа (0=полный, 1=компактный)")
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
        
        # 🚀 ОПТИМИЗАЦИЯ: Если запрос компактный - возвращаем сокращенный формат (-60-70% трафика)
        if compact and compact_history_response:
            # Передаём список напрямую, функция уже проверяет его тип
            return compact_history_response(history)
        
        return history
    except Exception as e:
        log_error(f"Ошибка получения истории сделок: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting trade history: {str(e)}")


# ============= WEBSOCKET ENDPOINTS =============

class ConnectionManager:
    """Менеджер WebSocket подключений для рассылки обновлений в реальном времени"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._broadcast_task = None
        
    async def connect(self, websocket: WebSocket):
        """Добавляет новое WebSocket подключение"""
        await websocket.accept()
        self.active_connections.append(websocket)
        log_info(f"[WS] Новое подключение. Всего активных: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Удаляет WebSocket подключение"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log_info(f"[WS] Подключение закрыто. Осталось активных: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправляет сообщение конкретному клиенту с обработкой ошибок"""
        try:
            await websocket.send_json(message)
        except ConnectionResetError as e:
            # Ошибка Windows: удаленный хост разорвал соединение
            log_info(f"[WS] Соединение было разорвано клиентом (ConnectionResetError)")
            self.disconnect(websocket)
        except Exception as e:
            log_error(f"[WS] Ошибка отправки персонального сообщения: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Рассылает сообщение всем подключенным клиентам с обработкой разорванных соединений"""
        disconnected = []
        
        for connection in list(self.active_connections):  # Создаем копию списка для безопасной итерации
            try:
                await connection.send_json(message)
            except ConnectionResetError:
                # Нормальная ошибка - клиент отключился на Windows
                log_info(f"[WS] Клиент отключился (ConnectionResetError), удаляем из списка")
                disconnected.append(connection)
            except (RuntimeError, OSError) as e:
                # Другие сетевые ошибки
                log_info(f"[WS] Сетевая ошибка при отправке сообщения: {type(e).__name__}")
                disconnected.append(connection)
            except Exception as e:
                log_error(f"[WS] Ошибка отправки сообщения клиенту: {e}")
                disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for conn in disconnected:
            self.disconnect(conn)
    
    async def start_broadcasting(self):
        """Запускает фоновую задачу для периодической рассылки данных"""
        if self._broadcast_task:
            return
        
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        log_info("[WS] Запущена фоновая рассылка данных")
    
    async def _broadcast_loop(self):
        """Фоновый цикл рассылки данных каждую секунду"""
        while True:
            try:
                if self.active_connections and trading_bot:
                    # Получаем свежие данные
                    data = await self._get_realtime_data()
                    if data:
                        await self.broadcast(data)
                
                # Ждем 1 секунду перед следующим обновлением
                await asyncio.sleep(1)
            except Exception as e:
                log_error(f"[WS] Ошибка в цикле рассылки: {e}")
                await asyncio.sleep(5)  # Пауза при ошибке
    
    async def _get_realtime_data(self) -> dict:
        """Получает актуальные данные для рассылки клиентам"""
        try:
            if not trading_bot:
                return None
            
            # Получаем активную пару
            symbol = trading_bot.settings.trading_pairs.get('active_pair', 'BTC/USDT')
            
            # Получаем данные о рынке
            ticker = trading_bot.exchange.get_ticker(symbol)
            if not ticker:
                log_error(f"[WS] Не удалось получить ticker для {symbol}")
                return None
            
            # 🔍 DEBUG: Логируем значение change для отладки
            change_24h = ticker.get('change', 0)
            log_info(f"[WS] Получены данные: symbol={symbol}, change_24h={change_24h}, ticker_keys={list(ticker.keys())}")
            
            # Формируем данные
            data = {
                "type": "market_update",
                "timestamp": datetime.now().isoformat(),
                "market": {
                    "symbol": symbol,
                    "current_price": ticker.get('last', 0),
                    "change_24h": ticker.get('change', 0)  # Используем 'change', как возвращает get_ticker()
                }
            }
            
            # Добавляем EMA данные если доступны
            try:
                latest_market = getattr(trading_bot, 'latest_market_data', None)
                strategy = getattr(trading_bot, 'strategy', None)

                ema_fast = None
                ema_slow = None
                ema_diff = None

                if latest_market:
                    ema_fast = latest_market.get('fast_ema')
                    ema_slow = latest_market.get('slow_ema')
                    ema_diff = latest_market.get('ema_diff_percent')
                    if ema_diff is not None:
                        ema_diff *= 100

                if ema_fast is None and strategy and hasattr(strategy, 'ema_fast'):
                    ema_fast = getattr(strategy, 'ema_fast', None)
                if ema_slow is None and strategy and hasattr(strategy, 'ema_slow'):
                    ema_slow = getattr(strategy, 'ema_slow', None)
                if ema_diff is None and strategy and hasattr(strategy, 'ema_diff_percent'):
                    ema_diff = getattr(strategy, 'ema_diff_percent', None)
                    if ema_diff is not None:
                        ema_diff *= 100

                if ema_fast and ema_slow and ema_diff is not None:
                    threshold = None
                    if strategy and hasattr(strategy, 'settings'):
                        threshold = strategy.settings.get('ema_threshold')
                    if threshold is None:
                        threshold = trading_bot.settings.strategy_settings.get('ema_threshold')
                    if threshold is None:
                        threshold = trading_bot.settings.settings.get('ema_cross_threshold', 0.005)
                    if threshold > 1:
                        threshold = threshold / 100
                    threshold_percent = threshold * 100

                    signal = "wait"
                    if ema_diff > threshold_percent:
                        signal = "buy"
                    elif ema_diff < -threshold_percent:
                        signal = "sell"

                    data["ema"] = {
                        "signal": signal,
                        "percent": ema_diff,
                        "text": "ВВЕРХ" if signal == "buy" else "ВНИЗ" if signal == "sell" else "НЕЙТРАЛЬНО"
                    }
            except Exception as e:
                log_error(f"[WS] Ошибка получения EMA: {e}")
            
            # Добавляем ML данные если доступны
            try:
                if hasattr(trading_bot, 'ml_model') and trading_bot.ml_model:
                    # Используем последний прогноз если доступен
                    if hasattr(trading_bot, 'last_ml_prediction'):
                        prediction = trading_bot.last_ml_prediction or 0.5
                        data["ml"] = {
                            "prediction": float(prediction),
                        }
            except Exception as e:
                log_error(f"[WS] Ошибка получения ML: {e}")
            
            # Добавляем данные о позициях
            try:
                import os
                from utils.position_manager import load_position_state
                
                # 🔧 ИСПОЛЬЗУЕМ АБСОЛЮТНЫЙ ПУТЬ К ФАЙЛУ СОСТОЯНИЯ
                position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
                state = load_position_state(position_state_path)
                if state:
                    total_positions = 0
                    for pair_symbol, pair_data in state.items():
                        if isinstance(pair_data, dict) and 'positions' in pair_data:
                            total_positions += len(pair_data.get('positions', []))
                    
                    if total_positions > 0:
                        data["positions"] = {
                            "open_count": total_positions
                        }
            except Exception as e:
                log_error(f"[WS] Ошибка получения позиций: {e}")
            
            return data
            
        except Exception as e:
            log_error(f"[WS] Ошибка получения данных в реальном времени: {e}")
            return None


# Создаем глобальный менеджер подключений
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для получения обновлений в реальном времени
    Клиент подключается к ws://server/ws и получает обновления каждую секунду
    """
    await manager.connect(websocket)
    
    # Запускаем фоновую рассылку, если еще не запущена
    if not manager._broadcast_task:
        await manager.start_broadcasting()
    
    try:
        # Отправляем начальное сообщение
        await manager.send_personal_message({
            "type": "connected",
            "message": "WebSocket подключен успешно",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # Ожидаем сообщений от клиента (для keep-alive)
        while True:
            try:
                data = await websocket.receive_text()
                # Можем обрабатывать команды от клиента, если нужно
                if data == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
            except ConnectionResetError:
                # Нормальное отключение на Windows
                log_info("[WS] Клиент отключился (ConnectionResetError)")
                break
            except RuntimeError as e:
                # Соединение закрыто
                log_info(f"[WS] Соединение закрыто: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log_info("[WS] Клиент отключился (WebSocketDisconnect)")
    except ConnectionResetError:
        # Обработка ошибки Windows
        manager.disconnect(websocket)
        log_info("[WS] Соединение было разорвано (ConnectionResetError)")
    except Exception as e:
        log_error(f"[WS] Ошибка WebSocket: {type(e).__name__}: {e}")
        manager.disconnect(websocket)
    finally:
        # Гарантированно удаляем соединение
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    log_info("[WEB] Запуск Web App сервера...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
