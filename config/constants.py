"""
КОНСТАНТЫ ПРОЕКТА
"""

# Торговые пары (только BTC и SOL по умолчанию)
TRADING_PAIRS = {
    'BTC/USDT': '(₿) Bitcoin',
    'SOL/USDT': '(◎) Solana'
}

# 🔧 ИСПРАВЛЕННЫЕ минимальные объемы торговли для KuCoin
MIN_TRADE_AMOUNTS = {
    'BTC/USDT': 0.00001,  # 🔧 ИСПРАВЛЕНО: 0.00001 BTC
    'SOL/USDT': 0.001,  # 🔧 ИСПРАВЛЕНО: минимум 0.001 SOL (не 0.1)
}

MIN_TRADE_USDT = 0.1  # Минимальная сумма в USDT

# Стратегии
STRATEGIES = {
    'ema_ml': '📈 EMA + ML',
    'price_action': '⚡ Price Action',
    'macd_rsi': '🎯 MACD + RSI',
    'bollinger': '📊 Bollinger Bands',
    'hybrid': '🔄 Гибридная'
}

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    'symbol': 'BTC/USDT',
    'trade_amount_percent': 0.1,  # 🔧 ВОЗВРАЩАЕМ 10% - теперь достаточно
    'ema_cross_threshold': 0.005,
    'price_update_frequency': 300,
    'enable_price_updates': True,
    'enable_trade_signals': True,
    'demo_mode': True,
    'trading_enabled': True,
}

# Настройки ML по умолчанию
DEFAULT_ML_SETTINGS = {
    'enabled': True,
    'confidence_threshold_buy': 0.4,
    'confidence_threshold_sell': 0.3,
    'retrain_frequency_hours': 24
}

# Настройки рисков по умолчанию
DEFAULT_RISK_SETTINGS = {
    'max_daily_loss': 3.0,
    # 🔧 УДАЛЕНО: stop_loss и take_profit теперь только в настройках стратегии
    'max_position_size': 25.0,
    'max_consecutive_losses': 3,
    'volatility_limit': 5.0,
    'min_trade_amount_usdt': 0.1  # Минимальная сумма сделки
}

# Таймфреймы
TIMEFRAMES = {
    '1m': '1 минута',
    '5m': '5 минут',
    '15m': '15 минут',
    '1h': '1 час',
    '4h': '4 часа',
    '1d': '1 день'
}

# Сообщения
MESSAGES = {
    'start': "🤖 <b>ТОРГОВЫЙ БОТ АКТИВИРОВАН</b>",
    'error': "❌ Ошибка",
    'processing': "⏳ Обрабатываю запрос...",
    'success': "✅ Успешно",
    'insufficient_funds': "❌ Недостаточно средств",
    'min_trade_amount': f"❌ Минимальная сумма сделки: {MIN_TRADE_USDT} USDT"
}