"""Тестируем исправленный fetch_my_trades"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.exchange import ExchangeManager

print("=" * 60)
print("ТЕСТ: Получение сделок через ExchangeManager")
print("=" * 60)

# Создаем экземпляр
exchange = ExchangeManager()

if not exchange.connected:
    print("❌ Нет подключения к бирже!")
    sys.exit(1)

print("✅ Подключение установлено\n")

# Тестируем fetch_my_trades
print("Вызываем fetch_my_trades для BTC/USDT...")
trades = exchange.fetch_my_trades('BTC/USDT', limit=500)

print(f"\n📊 Получено сделок: {len(trades)}")

if trades:
    print("\n🔍 ВСЕ СДЕЛКИ:")
    for i, trade in enumerate(trades, 1):
        print(f"{i}. {trade['datetime']} - {trade['side'].upper():4} {trade['amount']:.8f} BTC @ {trade['price']:,.2f} USDT")

# Теперь тестируем get_open_buy_trades_after_last_sell
print("\n" + "=" * 60)
print("ТЕСТ: Получение открытых позиций")
print("=" * 60)

open_trades, max_price = exchange.get_open_buy_trades_after_last_sell('BTC/USDT')

print(f"\n📈 ОТКРЫТЫХ ПОЗИЦИЙ: {len(open_trades)}")
print(f"💰 Максимальная цена: {max_price:,.2f} USDT\n")

if open_trades:
    print("🔍 ДЕТАЛИ ОТКРЫТЫХ ПОЗИЦИЙ:")
    total_cost = 0
    for i, trade in enumerate(open_trades, 1):
        cost = trade.get('cost', 0)
        total_cost += cost
        print(f"{i}. Цена входа: {trade['price']:,.2f} USDT")
        print(f"   Количество: {trade['amount']:.8f} BTC")
        print(f"   Стоимость: {cost:.2f} USDT")
        print(f"   Время: {trade['timestamp']}\n")
    
    print(f"💵 ОБЩАЯ СТОИМОСТЬ ПОЗИЦИЙ: {total_cost:.2f} USDT")
else:
    print("⚠️ Открытых позиций не найдено!")
