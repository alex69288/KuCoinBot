"""Проверяем, что вообще возвращает API без limit"""
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
print("ПРОВЕРКА: fetch_my_trades с разными limit")
print("=" * 60)

for test_limit in [None, 1, 10, 50, 100, 500]:
    print(f"\n📊 limit={test_limit}")
    try:
        trades = ex.fetch_my_trades('BTC/USDT', limit=test_limit)
        print(f"   ✅ Получено: {len(trades)} сделок")
        if trades:
            print(f"   🕐 Первая: {trades[0]['datetime']} ({trades[0]['side']})")
            if len(trades) > 1:
                print(f"   🕐 Последняя: {trades[-1]['datetime']} ({trades[-1]['side']})")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

# Проверим прямой запрос к API
print("\n" + "=" * 60)
print("ПРЯМОЙ ЗАПРОС К API (private_get_fills)")
print("=" * 60)

try:
    # Прямой вызов KuCoin API
    response = ex.privateGetFills()
    fills = response.get('data', {}).get('items', [])
    print(f"✅ Получено через прямой API: {len(fills)} сделок")
    
    if fills:
        print("\n🔍 Все сделки из прямого API:")
        for i, fill in enumerate(fills, 1):
            side = fill.get('side', 'unknown')
            price = float(fill.get('price', 0))
            size = float(fill.get('size', 0))
            created_at = fill.get('createdAt', 0)
            print(f"{i}. {created_at} - {side.upper()} {size:.8f} BTC @ {price:,.2f} USDT")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
