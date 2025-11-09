"""
БЫСТРЫЙ ТЕСТ ПОЛУЧЕНИЯ РЫНОЧНЫХ ДАННЫХ
Запуск: python debug_fetch.py
"""
import time
from core.exchange import ExchangeManager
from utils.logger import log_info, log_error

SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'

if __name__ == '__main__':
    log_info('🔬 Старт теста получения рыночных данных...')
    ex = ExchangeManager()
    if not ex.connected:
        log_error('❌ Нет подключения к бирже, проверяйте ключи/сеть/прокси.')
    else:
        data = ex.get_market_data(SYMBOL, timeframe=TIMEFRAME, limit=50)
        if data:
            log_info(f"✅ Успех: цена={data['current_price']}, EMA_diff={data['ema_diff_percent']:.6f}, свечей={len(data['ohlcv'])}")
        else:
            log_error('❌ Не удалось получить данные даже после повторных попыток. Смотрите логи выше.')
    log_info('🧪 Тест завершен.')
