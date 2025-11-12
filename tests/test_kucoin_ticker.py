"""
Тестовый скрипт для проверки данных тикера KuCoin
Проверяет какие поля возвращаются методом fetch_ticker
"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_kucoin_ticker():
    """Тестирование данных тикера KuCoin"""
    print("🔍 Тестирование тикера KuCoin API...")
    print("=" * 60)
    
    try:
        # Создаем клиент KuCoin
        api_key = os.getenv('KUCOIN_API_KEY', '')
        secret_key = os.getenv('KUCOIN_SECRET_KEY', '')
        passphrase = os.getenv('KUCOIN_PASSPHRASE', '')
        
        exchange = ccxt.kucoin({
            'apiKey': api_key,
            'secret': secret_key,
            'password': passphrase,
            'enableRateLimit': True
        })
        
        # Загружаем рынки
        exchange.load_markets()
        print("✅ Подключение к KuCoin успешно")
        
        # Получаем тикер для BTC/USDT
        symbol = 'BTC/USDT'
        print(f"\n📊 Запрос тикера для {symbol}...")
        ticker = exchange.fetch_ticker(symbol)
        
        print("\n🔍 Все доступные поля тикера:")
        print("-" * 60)
        for key, value in ticker.items():
            print(f"  {key:20s}: {value}")
        
        print("\n" + "=" * 60)
        print("📈 Анализ полей изменения цены:")
        print("-" * 60)
        
        # Проверяем все возможные поля для 24h change
        possible_fields = [
            'change', 'percentage', 'percentageChange',
            'changePercent', 'priceChange', 'priceChangePercent',
            'changeRate', 'changePrice'
        ]
        
        for field in possible_fields:
            if field in ticker and ticker[field] is not None:
                print(f"  ✅ {field:25s}: {ticker[field]}")
            else:
                print(f"  ❌ {field:25s}: Не найдено")
        
        # Дополнительно проверяем, есть ли данные о high/low 24h
        print("\n📊 Дополнительные поля 24h:")
        print("-" * 60)
        fields_24h = ['high', 'low', 'baseVolume', 'quoteVolume']
        for field in fields_24h:
            if field in ticker and ticker[field] is not None:
                print(f"  ✅ {field:25s}: {ticker[field]}")
            else:
                print(f"  ❌ {field:25s}: Не найдено")
        
        # Рассчитываем изменение вручную для сравнения
        if 'last' in ticker and 'open' in ticker and ticker['open']:
            manual_change = ((ticker['last'] - ticker['open']) / ticker['open']) * 100
            print(f"\n🔢 Вручную рассчитанное изменение:")
            print(f"  Цена открытия: {ticker.get('open', 0):.2f} USDT")
            print(f"  Текущая цена:   {ticker.get('last', 0):.2f} USDT")
            print(f"  Изменение:      {manual_change:+.2f}%")
            
            if 'percentage' in ticker and ticker['percentage'] is not None:
                print(f"  API percentage: {ticker['percentage']:+.2f}%")
                diff = abs(manual_change - ticker['percentage'])
                if diff < 0.01:
                    print(f"  ✅ Совпадение с API (разница: {diff:.4f}%)")
                else:
                    print(f"  ⚠️  Расхождение с API (разница: {diff:.4f}%)")
        
        print("\n" + "=" * 60)
        print("✅ Тест завершен успешно")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_kucoin_ticker()
