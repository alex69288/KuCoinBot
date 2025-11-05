"""
ТЕСТИРОВАНИЕ С TAKE PROFIT 0.30%
Оптимизация Stop Loss
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

# Параметры теста (общие для всех вариантов)
symbol = 'BTC/USDT'
timeframe = '1h'
days = 30
initial_balance = 100.0
size_percent = 0.08  # 8%

# Варианты для тестирования с TP 0.30%
test_variants = [
    {'tp': 0.30, 'sl': 0.80, 'name': 'Вариант 1 (Узкий SL)'},
    {'tp': 0.30, 'sl': 0.90, 'name': 'Вариант 2 (Средний SL)'},
    {'tp': 0.30, 'sl': 1.00, 'name': 'Вариант 3 (Широкий SL)'},
    {'tp': 0.30, 'sl': 1.20, 'name': 'Вариант 4 (Очень широкий SL)'},
]

results_summary = []

for variant in test_variants:
    tp = variant['tp']
    sl = variant['sl']
    name = variant['name']
    
    print()
    print("=" * 70)
    print(f"🧪 {name}")
    print("=" * 70)
    print(f"📈 Take Profit: {tp}% | 🛑 Stop Loss: {sl}%")
    print()
    
    # Создаем стратегию
    strategy = EmaMlStrategy()
    
    # Обновляем параметры
    strategy.settings['take_profit_percent'] = tp
    strategy.settings['stop_loss_percent'] = sl
    strategy.settings['ema_threshold'] = 0.0025
    
    # Запускаем бэктест
    engine = BacktestEngine(initial_balance=initial_balance, size_percent=size_percent)
    stats = engine.run_backtest(strategy, symbol, timeframe, days)
    
    # Сохраняем результаты
    if stats:
        result = {
            'name': name,
            'tp': tp,
            'sl': sl,
            'final_balance': stats.get('final_balance', 0),
            'total_profit': stats.get('total_profit', 0),
            'total_profit_percent': stats.get('total_profit_percent', 0),
            'total_trades': stats.get('total_trades', 0),
            'wins': stats.get('wins', 0),
            'losses': stats.get('losses', 0),
            'win_rate': stats.get('win_rate', 0),
            'avg_profit': stats.get('avg_profit', 0),
            'max_profit': stats.get('max_profit', 0),
            'max_loss': stats.get('max_loss', 0),
            'profit_factor': stats.get('profit_factor', 0),
        }
        results_summary.append(result)

# Выводим сравнительный анализ
print()
print()
print("=" * 70)
print("📊 СРАВНИТЕЛЬНЫЙ АНАЛИЗ (TP = 0.30%)")
print("=" * 70)
print()

for result in results_summary:
    print(f"\n{result['name']}")
    print(f"  TP: {result['tp']}% | SL: {result['sl']}%")
    print(f"  Финальный баланс: {result['final_balance']:.2f} USDT | Прибыль: {result['total_profit_percent']:.2f}%")
    print(f"  Сделок: {result['total_trades']} | Win Rate: {result['win_rate']:.1f}%")
    print(f"  Avg Profit/Loss: {result['avg_profit']:.4f} USDT | Max Profit: {result['max_profit']:.4f} USDT | Max Loss: {result['max_loss']:.4f} USDT")
    print(f"  Profit Factor: {result['profit_factor']:.2f}")

# Определяем лучший вариант
if results_summary:
    best = max(results_summary, key=lambda x: x['profit_factor'])
    print()
    print("=" * 70)
    print(f"🏆 ЛУЧШИЙ ВАРИАНТ: {best['name']}")
    print(f"   Take Profit: {best['tp']}% | Stop Loss: {best['sl']}%")
    print(f"   Profit Factor: {best['profit_factor']:.2f}")
    print(f"   Прибыль: {best['total_profit_percent']:.2f}%")
    print("=" * 70)
