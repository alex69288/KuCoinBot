import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
import uvicorn
import socketio
from loguru import logger
from fastapi import APIRouter
from core.exchange import ExchangeManager
from core.bot import TradingBot
from core.risk_manager import RiskManager
from typing import Optional

# Загружаем переменные окружения
load_dotenv()

# Инициализация Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Lifespan для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting backend server")
    await initialize_exchange_and_bot()
    # asyncio.create_task(start_websocket_broadcasting())  # Временно отключено для тестирования
    yield
    # Shutdown
    logger.info("🛑 Shutting down backend server")

app = FastAPI(lifespan=lifespan, title="KuCoin Trading Bot", version="0.1.0")

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Глобальные переменные для Exchange и Bot
exchange: Optional[ExchangeManager] = None
trading_bot: Optional[TradingBot] = None

async def initialize_exchange_and_bot():
    global exchange, trading_bot
    try:
        api_key = os.getenv('KUCOIN_API_KEY')
        api_secret = os.getenv('KUCOIN_API_SECRET')
        api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
        testnet = os.getenv('KUCOIN_TESTNET', 'false').lower() == 'true'

        if api_key and api_secret and api_passphrase:
            exchange = ExchangeManager({
                'api_key': api_key,
                'api_secret': api_secret,
                'api_passphrase': api_passphrase,
                'testnet': testnet
            })

            risk_manager = RiskManager()
            trading_bot = TradingBot(exchange, risk_manager, {
                'symbol': os.getenv('TRADING_SYMBOL', 'BTC/USDT'),
                'timeframe': os.getenv('TRADING_TIMEFRAME', '1h'),
                'trading_enabled': False,
                'strategy': 'ema_ml'
            })

            logger.info('✅ Exchange and Trading Bot initialized')
        else:
            logger.warning('⚠️ KuCoin credentials not found, running in mock mode')
    except Exception as e:
        logger.error(f'Failed to initialize Exchange/Bot: {e}')

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": "2024-01-01T00:00:00Z"}

# API Router
api_router = APIRouter(prefix="/api")

# Status routes
@api_router.get("/status")
@limiter.limit("100/minute")
async def get_status(request: Request):
    try:
        if not trading_bot:
            return {
                "isRunning": False,
                "tradingEnabled": False,
                "balance": {
                    "total": 0,
                    "available": 0,
                    "used": 0,
                    "currency": "USDT"
                },
                "positions": {
                    "current": None,
                    "total": 0,
                    "profit": 0
                },
                "uptime": 0,
                "timestamp": "2024-01-01T00:00:00Z",
                "error": "Bot not initialized (missing API credentials)"
            }

        status = await trading_bot.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

# Market routes
@api_router.get("/market")
@limiter.limit("100/minute")
async def get_market_data(request: Request):
    try:
        if not trading_bot:
            return {
                "symbol": "BTC/USDT",
                "price": 45000,
                "change24h": 0,
                "changePercent24h": 0,
                "volume": 0,
                "volume24h": 0,
                "high24h": 45000,
                "low24h": 45000,
                "timestamp": "2024-01-01T00:00:00Z",
                "error": "Bot not initialized (missing API credentials)"
            }

        market_data = await trading_bot.get_market_data()
        return market_data
    except Exception as e:
        logger.error(f"Failed to get market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market data")

# Trade routes
@api_router.post("/trade/start")
@limiter.limit("10/minute")
async def start_trading(request: Request):
    try:
        if not trading_bot:
            return {
                "success": False,
                "message": "Bot running in mock mode (no API credentials)",
                "mockMode": True
            }

        if not trading_bot.is_active():
            await trading_bot.start()

        trading_bot.enable_trading()
        logger.info("✅ Trading started")
        return {"success": True, "message": "Trading started"}
    except Exception as e:
        logger.error(f"Failed to start trading: {e}")
        raise HTTPException(status_code=500, detail="Failed to start trading")

@api_router.post("/trade/stop")
@limiter.limit("10/minute")
async def stop_trading(request: Request):
    try:
        if not trading_bot:
            return {
                "success": False,
                "message": "Bot running in mock mode",
                "mockMode": True
            }

        trading_bot.disable_trading()
        logger.info("⚠️ Trading stopped")
        return {"success": True, "message": "Trading stopped"}
    except Exception as e:
        logger.error(f"Failed to stop trading: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop trading")

@api_router.post("/trade/bot/start")
@limiter.limit("10/minute")
async def start_bot(request: Request):
    try:
        if not trading_bot:
            return {
                "success": False,
                "message": "Bot running in mock mode",
                "mockMode": True
            }

        await trading_bot.start()
        logger.info("🚀 Bot started")
        return {"success": True, "message": "Bot started (trading disabled)"}
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise HTTPException(status_code=500, detail="Failed to start bot")

@api_router.post("/trade/bot/stop")
@limiter.limit("10/minute")
async def stop_bot(request: Request):
    try:
        if not trading_bot:
            return {
                "success": False,
                "message": "Bot running in mock mode",
                "mockMode": True
            }

        trading_bot.stop()
        logger.info("🛑 Bot stopped")
        return {"success": True, "message": "Bot stopped completely"}
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop bot")

# Settings routes
@api_router.get("/settings")
@limiter.limit("50/minute")
async def get_settings(request: Request):
    try:
        # TODO: Получить реальные настройки
        settings = {
            "strategy": "ema_ml",
            "riskLevel": "medium",
            "maxPositionSize": 100,
            "stopLoss": 2,
            "takeProfit": 5,
            "mlEnabled": True
        }
        return settings
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@api_router.put("/settings")
@limiter.limit("10/minute")
async def update_settings(settings: dict, request: Request):
    try:
        # TODO: Сохранить настройки
        logger.info(f"Settings updated: {settings}")
        return {"success": True, "settings": settings}
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

# Include API router
app.include_router(api_router)

# WebSocket broadcasting
async def start_websocket_broadcasting():
    while True:
        if trading_bot:
            try:
                status = await trading_bot.get_status()
                await sio.emit('status', status)
            except Exception as error:
                logger.error(f'Failed to broadcast status: {error}')

            try:
                market_data = await trading_bot.get_market_data()
                await sio.emit('market', market_data)
            except Exception as error:
                logger.error(f'Failed to broadcast market data: {error}')

        await asyncio.sleep(5)  # Каждые 5 секунд

# Socket.IO events
@sio.event
async def connect(sid, environ):
    logger.info(f'WebSocket client connected: {sid}')
    if trading_bot:
        try:
            status = await trading_bot.get_status()
            await sio.emit('status', status, to=sid)
        except Exception as err:
            logger.error(f'Failed to send initial status: {err}')

@sio.event
async def disconnect(sid):
    logger.info(f'WebSocket client disconnected: {sid}')

# Mount Socket.IO to FastAPI
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    port = 3001  # Жестко заданный порт для тестирования
    uvicorn.run(app, host="0.0.0.0", port=port)