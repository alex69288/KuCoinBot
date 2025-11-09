"""Проверяем открытые ордера и позиции на KuCoin"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True
})

print("=" * 60)
print("ПРОВЕРКА: Открытые ордера на KuCoin")
print("=" * 60)

# 1. Открытые ордера
print("\n1️⃣ ОТКРЫТЫЕ ОРДЕРА (fetch_open_orders)")
try:
    orders = ex.fetch_open_orders('BTC/USDT')
    print(f"✅ Открытых ордеров: {len(orders)}")
    if orders:
        for i, order in enumerate(orders, 1):
            print(f"\n   Ордер {i}:")
            print(f"   ID: {order['id']}")
            print(f"   Тип: {order['type']} {order['side']}")
            print(f"   Цена: {order['price']}")
            print(f"   Количество: {order['amount']}")
            print(f"   Статус: {order['status']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. Все ордера (включая закрытые)
print("\n2️⃣ ВСЕ ОРДЕРА (fetch_orders)")
try:
    orders = ex.fetch_orders('BTC/USDT', limit=50)
    print(f"✅ Всего ордеров: {len(orders)}")
    if orders:
        print("\n   📋 Список ордеров:")
        for i, order in enumerate(orders, 1):
            print(f"   {i}. {order['datetime']} - {order['side'].upper()} {order['type']} @ {order.get('price', 0):,.2f} - {order['status']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. Баланс
print("\n3️⃣ БАЛАНС")
try:
    balance = ex.fetch_balance()
    btc_balance = balance.get('BTC', {})
    usdt_balance = balance.get('USDT', {})
    
    print(f"✅ BTC:")
    print(f"   Total: {btc_balance.get('total', 0):.8f}")
    print(f"   Free: {btc_balance.get('free', 0):.8f}")
    print(f"   Used: {btc_balance.get('used', 0):.8f}")
    
    print(f"\n✅ USDT:")
    print(f"   Total: {usdt_balance.get('total', 0):.2f}")
    print(f"   Free: {usdt_balance.get('free', 0):.2f}")
    print(f"   Used: {usdt_balance.get('used', 0):.2f}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# 4. Проверим закрытые ордера
print("\n4️⃣ ЗАКРЫТЫЕ ОРДЕРА (fetch_closed_orders)")
try:
    orders = ex.fetch_closed_orders('BTC/USDT', limit=50)
    print(f"✅ Закрытых ордеров: {len(orders)}")
    if orders:
        print("\n   📋 Последние закрытые ордера:")
        for i, order in enumerate(orders[:10], 1):
            filled = order.get('filled', 0)
            print(f"   {i}. {order['datetime']} - {order['side'].upper()} {filled:.8f} BTC @ {order.get('price', 0):,.2f}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
