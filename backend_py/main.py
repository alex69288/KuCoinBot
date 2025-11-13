import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
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
    asyncio.create_task(start_websocket_broadcasting())
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
exchange = None
trading_bot = None

async def initialize_exchange_and_bot():
    global exchange, trading_bot
    try:
        api_key = os.getenv('KUCOIN_API_KEY', '')
        api_secret = os.getenv('KUCOIN_API_SECRET', '')
        api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE', '')
        testnet = os.getenv('KUCOIN_TESTNET', 'false').lower() == 'true'

        if api_key and api_secret and api_passphrase:
            # Импорт здесь, чтобы избежать циклических импортов
            from core.exchange import ExchangeManager
            from core.bot import TradingBot

            exchange = ExchangeManager({
                'apiKey': api_key,
                'apiSecret': api_secret,
                'apiPassphrase': api_passphrase,
                'testnet': testnet
            })

            trading_bot = TradingBot(exchange, {
                'symbol': os.getenv('TRADING_SYMBOL', 'BTC/USDT'),
                'timeframe': os.getenv('TRADING_TIMEFRAME', '1h'),
                'trading_enabled': False,
                'strategy': 'ema_ml'
            })

            logger.info('✅ Exchange and Trading Bot initialized')
        else:
            logger.warning('⚠️ KuCoin credentials not found, running in mock mode')
    except Exception as error:
        logger.error(f'Failed to initialize Exchange/Bot: {error}')

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": "2025-11-13T16:50:00Z"}  # Использовать datetime

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
    port = int(os.getenv('PORT', 3000))
    uvicorn.run(socket_app, host="0.0.0.0", port=port)