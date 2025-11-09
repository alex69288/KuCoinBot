"""Проверяем все возможные источники истории на KuCoin"""
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

print("=" * 70)
print("ПОИСК ВСЕХ СДЕЛОК BTC/USDT")
print("=" * 70)

# Метод 1: fetch_my_trades с разными параметрами
print("\n1️⃣ fetch_my_trades (стандартный)")
trades = ex.fetch_my_trades('BTC/USDT')
print(f"   Получено: {len(trades)} сделок")

# Метод 2: fetch_closed_orders
print("\n2️⃣ fetch_closed_orders")
try:
    orders = ex.fetch_closed_orders('BTC/USDT', limit=100)
    print(f"   Получено: {len(orders)} ордеров")
    for o in orders:
        print(f"   - {o['datetime']} {o['side'].upper()} {o['filled']:.8f} @ {o.get('price', 0):,.2f}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Метод 3: Прямой запрос к /api/v1/orders (все ордера)
print("\n3️⃣ privateGetOrders (все ордера за 7 дней)")
try:
    import time
    params = {
        'symbol': 'BTC-USDT',
        'status': 'done',  # done = закрытые
        'startAt': int(time.time() - 7*86400) * 1000,  # 7 дней назад в ms
    }
    response = ex.privateGetOrders(params)
    items = response.get('data', {}).get('items', [])
    print(f"   Получено: {len(items)} ордеров")
    for item in items:
        side = item.get('side', 'unknown')
        price = item.get('price', '0')
        size = item.get('size', '0')
        created = item.get('createdAt', 0)
        print(f"   - {created} {side.upper()} {size} @ {price}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Метод 4: Прямой запрос к /api/v1/fills (все fills)
print("\n4️⃣ privateGetFills (детали исполнения)")
try:
    params = {
        'symbol': 'BTC-USDT',
    }
    response = ex.privateGetFills(params)
    items = response.get('data', {}).get('items', [])
    print(f"   Получено: {len(items)} fills")
    for item in items:
        side = item.get('side', 'unknown')
        price = item.get('price', '0')
        size = item.get('size', '0')
        created = item.get('createdAt', 0)
        print(f"   - {created} {side.upper()} {size} @ {price}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Метод 5: Историческиеордера с пагинацией
print("\n5️⃣ privateGetOrders с пагинацией")
try:
    params = {
        'symbol': 'BTC-USDT',
        'status': 'done',
    }
    all_orders = []
    page = 1
    
    while page <= 5:  # Максимум 5 страниц
        params['currentPage'] = page
        params['pageSize'] = 500
        response = ex.privateGetOrders(params)
        items = response.get('data', {}).get('items', [])
        
        if not items:
            break
            
        all_orders.extend(items)
        print(f"   Страница {page}: {len(items)} ордеров")
        
        total_pages = response.get('data', {}).get('totalPage', 1)
        if page >= total_pages:
            break
            
        page += 1
    
    print(f"\n   📊 Всего ордеров: {len(all_orders)}")
    if all_orders:
        print("\n   📋 Список всех ордеров:")
        for i, item in enumerate(all_orders, 1):
            side = item.get('side', 'unknown')
            price = item.get('price', '0')
            size = item.get('size', '0')
            created = item.get('createdAt', 0)
            deal_size = item.get('dealSize', '0')
            print(f"   {i}. {created} {side.upper()} {deal_size}/{size} @ {price}")
            
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
