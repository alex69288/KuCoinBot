"""Тест: проверяем разные варианты params"""
import ccxt
import os
import time
from dotenv import load_dotenv

load_dotenv()

ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True
})

print("=" * 60)
print("ПРОВЕРКА: Какие параметры работают с KuCoin API")
print("=" * 60)

# Тест 1: Вообще без параметров
print("\n1️⃣ БЕЗ ПАРАМЕТРОВ (только limit)")
try:
    trades = ex.fetch_my_trades('BTC/USDT', limit=500)
    print(f"✅ Получено: {len(trades)} сделок")
    if trades:
        print(f"   Последняя: {trades[0]['datetime']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 2: С pageSize но БЕЗ startAt
print("\n2️⃣ С pageSize, БЕЗ startAt")
try:
    params = {'pageSize': 500}
    trades = ex.fetch_my_trades('BTC/USDT', limit=500, params=params)
    print(f"✅ Получено: {len(trades)} сделок")
    if trades:
        print(f"   Последняя: {trades[0]['datetime']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 3: Только с startAt (без pageSize)
print("\n3️⃣ ТОЛЬКО startAt (без pageSize)")
try:
    # 7 дней назад
    startAt = int(time.time()) - (7 * 86400)
    params = {'startAt': startAt}
    trades = ex.fetch_my_trades('BTC/USDT', params=params)
    print(f"✅ Получено: {len(trades)} сделок")
    if trades:
        print(f"   Последняя: {trades[0]['datetime']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 4: pageSize + startAt (7 дней)
print("\n4️⃣ pageSize + startAt (7 дней назад)")
try:
    startAt = int(time.time()) - (7 * 86400)
    params = {'pageSize': 500, 'startAt': startAt}
    trades = ex.fetch_my_trades('BTC/USDT', limit=500, params=params)
    print(f"✅ Получено: {len(trades)} сделок")
    if trades:
        print(f"   Последняя: {trades[0]['datetime']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 5: pageSize + startAt (1 день)
print("\n5️⃣ pageSize + startAt (1 день назад)")
try:
    startAt = int(time.time()) - (1 * 86400)
    params = {'pageSize': 500, 'startAt': startAt}
    trades = ex.fetch_my_trades('BTC/USDT', limit=500, params=params)
    print(f"✅ Получено: {len(trades)} сделок")
    if trades:
        print(f"   Последняя: {trades[0]['datetime']}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "=" * 60)
print(f"Текущее время: {time.time()}")
print(f"7 дней назад: {time.time() - 7*86400}")
print(f"60 дней назад: {time.time() - 60*86400}")
