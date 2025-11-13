from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

from .config import Settings
from .core.exchange import ExchangeManager
from .core.bot import TradingBot
from .core.risk_manager import RiskManager
from .services.ml_service import MLService
from .database.session import get_db_session
from .database.repositories import TradingRepository

class Container(containers.DeclarativeContainer):
    """Dependency injection container"""

    # Configuration
    config = providers.Singleton(Settings)

    # Database
    db_session = providers.Factory(get_db_session, config=config)

    # Repositories
    trading_repository = providers.Factory(TradingRepository, session=db_session)

    # Core services
    exchange_manager = providers.Singleton(
        ExchangeManager,
        api_key=config.provided.kucoin_api_key,
        api_secret=config.provided.kucoin_api_secret,
        api_passphrase=config.provided.kucoin_api_passphrase,
        testnet=config.provided.kucoin_testnet,
    )

    risk_manager = providers.Singleton(RiskManager)

    ml_service = providers.Singleton(
        MLService,
        base_url=config.provided.ml_service_url,
    )

    trading_bot = providers.Singleton(
        TradingBot,
        exchange=exchange_manager,
        risk_manager=risk_manager,
        ml_service=ml_service,
        symbol=config.provided.trading_symbol,
        timeframe=config.provided.trading_timeframe,
        trading_enabled=config.provided.trading_enabled,
        strategy=config.provided.strategy,
    )

# Create container instance
container = Container()