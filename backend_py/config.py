from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # KuCoin API
    kucoin_api_key: Optional[str] = None
    kucoin_api_secret: Optional[str] = None
    kucoin_api_passphrase: Optional[str] = None
    kucoin_testnet: bool = False

    # Trading
    trading_symbol: str = "BTC/USDT"
    trading_timeframe: str = "1h"
    trading_enabled: bool = False
    strategy: str = "ema_ml"

    # Server
    port: int = 3000
    frontend_url: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_window_ms: int = 60000
    rate_limit_max_requests: int = 100

    # Database
    database_url: str = "sqlite+aiosqlite:///./trading_bot.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # ML Service
    ml_service_url: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()