"""Тестовый скрипт для проверки fetch_my_trades с параметрами"""
import ccxt
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Создаем exchange
ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True
})

# Проверяем с разными параметрами
days_back = 60
since_ms = int((time.time() - days_back * 86400) * 1000)
since_sec = since_ms // 1000

print(f"since_ms = {since_ms}")
print(f"since_sec = {since_sec}")
print(f"Текущее время (сек): {int(time.time())}\n")

# Тест 1: Без параметров
print("=" * 50)
print("ТЕСТ 1: fetch_my_trades без параметров")
try:
    trades = ex.fetch_my_trades('BTC/USDT', limit=10)
    print(f"✅ Получено {len(trades)} сделок")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 2: С since
print("\n" + "=" * 50)
print("ТЕСТ 2: fetch_my_trades с since (ms)")
try:
    trades = ex.fetch_my_trades('BTC/USDT', since=since_ms, limit=10)
    print(f"✅ Получено {len(trades)} сделок")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 3: С KuCoin параметрами
print("\n" + "=" * 50)
print("ТЕСТ 3: fetch_my_trades с KuCoin params (startAt)")
try:
    params = {
        'pageSize': 500,
        'startAt': since_sec
    }
    trades = ex.fetch_my_trades('BTC/USDT', since=since_ms, limit=10, params=params)
    print(f"✅ Получено {len(trades)} сделок")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Тест 4: Только params без since
print("\n" + "=" * 50)
print("ТЕСТ 4: fetch_my_trades только с params (без since)")
try:
    params = {
        'pageSize': 500,
        'startAt': since_sec
    }
    trades = ex.fetch_my_trades('BTC/USDT', params=params)
    print(f"✅ Получено {len(trades)} сделок")
except Exception as e:
    print(f"❌ Ошибка: {e}")
