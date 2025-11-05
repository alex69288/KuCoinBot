"""
АВТОМАТИЧЕСКИЙ ТЕСТ С РЕКОМЕНДУЕМЫМИ ПАРАМЕТРАМИ
"""
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, '.')

from test_backtest import BacktestEngine
from strategies.ema_ml import EmaMlStrategy

# Рекомендуемые параметры
params = {
    'take_profit_percent': 0.35,  # 0.35%
    'stop_loss_percent': 1.25,    # 1.25%
    'ema_threshold': 0.0025,      # 0.25%
}

# Параметры теста
symbol = 'BTC/USDT'
timeframe = '1h'
days = 30
initial_balance = 100.0
size_percent = 0.08  # 8%

# Создаем стратегию
strategy = EmaMlStrategy()

# Обновляем параметры
for key, value in params.items():
    if key in strategy.settings:
        strategy.settings[key] = value

print("=" * 60)
print("🧪 АВТОМАТИЧЕСКИЙ БЭКТЕСТИНГ")
print("=" * 60)
print()
print("⚙️ ПАРАМЕТРЫ ТЕСТА:")
print(f"💱 Пара: {symbol}")
print(f"📊 Таймфрейм: {timeframe}")
print(f"📅 Период: {days} дней")
print(f"💰 Начальный баланс: {initial_balance:.2f} USDT")
print(f"📊 Размер ставки: {size_percent * 100:.1f}%")
print()
print("🎯 ПАРАМЕТРЫ СТРАТЕГИИ:")
print(f"📈 Take Profit: {strategy.settings['take_profit_percent']:.4f}%")
print(f"🛑 Stop Loss: {strategy.settings['stop_loss_percent']:.2f}%")
print(f"📊 EMA Threshold: {strategy.settings['ema_threshold'] * 100:.2f}%")
print()
print("=" * 60)
print("🚀 ЗАПУСК БЭКТЕСТИНГА...")
print("=" * 60)
print()

# Запускаем бэктест
engine = BacktestEngine(initial_balance=initial_balance, size_percent=size_percent)
stats = engine.run_backtest(strategy, symbol, timeframe, days)

# Выводим результаты
if stats:
    print()
    print("✅ ТЕСТ ЗАВЕРШЕН!")
