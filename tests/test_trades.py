"""Тестовый скрипт для проверки получения сделок с KuCoin"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# Создаем exchange
ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True
})

# Пробуем получить сделки
print("Пытаемся получить сделки BTC/USDT...")
try:
    trades = ex.fetch_my_trades('BTC/USDT', limit=10)
    print(f"✅ Получено {len(trades)} сделок")
    
    if trades:
        print("\nПоследние 5 сделок:")
        for i, t in enumerate(trades[:5], 1):
            print(f"{i}. {t['datetime']} - {t['side'].upper()} {t['amount']} BTC @ {t['price']} USDT")
    else:
        print("⚠️ Сделки не найдены. Проверьте:")
        print("  - Есть ли реальные сделки на бирже?")
        print("  - Правильно ли указан символ (BTC/USDT)?")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
