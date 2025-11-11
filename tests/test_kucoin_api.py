"""
Тест подключения к KuCoin API
"""
import os
import sys
import asyncio
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    import ccxt
    from dotenv import load_dotenv
except ImportError as e:
    print(f"ОШИБКА: Не удалось импортировать необходимые модули: {e}")
    sys.exit(1)

# Загружаем переменные окружения
load_dotenv()

def test_kucoin_connection():
    """Тест подключения к KuCoin"""
    print("=" * 50)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К KUCOIN API")
    print("=" * 50)
    
    # Получаем учетные данные
    api_key = os.getenv('KUCOIN_API_KEY')
    secret_key = os.getenv('KUCOIN_SECRET_KEY')
    passphrase = os.getenv('KUCOIN_PASSPHRASE')
    
    if not all([api_key, secret_key, passphrase]):
        print("✗ ОШИБКА: Не все учетные данные API установлены")
        return False
    
    print(f"API Key: {api_key[:8]}...")
    print(f"Secret Key: {secret_key[:8]}...")
    print(f"Passphrase: ***")
    print()
    
    try:
        # Создаем экземпляр биржи
        print("Создание экземпляра биржи...")
        exchange = ccxt.kucoin({
            'apiKey': api_key,
            'secret': secret_key,
            'password': passphrase,
            'enableRateLimit': True,
        })
        print("✓ Экземпляр биржи создан")
        print()
        
        # Проверяем подключение через загрузку рынков
        print("Загрузка данных о рынках...")
        markets = exchange.load_markets()
        print(f"✓ Загружено {len(markets)} торговых пар")
        print()
        
        # Получаем информацию о балансе
        print("Получение информации о балансе...")
        balance = exchange.fetch_balance()
        
        print("✓ Баланс получен успешно")
        print()
        print("Доступные средства:")
        
        # Показываем только не нулевые балансы
        non_zero_balances = {
            currency: amounts 
            for currency, amounts in balance.items() 
            if isinstance(amounts, dict) and amounts.get('total', 0) > 0
        }
        
        if non_zero_balances:
            for currency, amounts in non_zero_balances.items():
                free = amounts.get('free', 0)
                used = amounts.get('used', 0)
                total = amounts.get('total', 0)
                if total > 0:
                    print(f"  {currency}:")
                    print(f"    Свободно: {free}")
                    print(f"    В ордерах: {used}")
                    print(f"    Всего: {total}")
        else:
            print("  (Нет средств на балансе)")
        
        print()
        
        # Получаем тикер для популярной пары
        print("Получение тикера BTC/USDT...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✓ Текущая цена BTC/USDT: ${ticker['last']:,.2f}")
        print(f"  24ч объем: ${ticker['quoteVolume']:,.2f}")
        print()
        
        print("=" * 50)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Подключение к KuCoin API работает корректно")
        print("=" * 50)
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"✗ ОШИБКА АУТЕНТИФИКАЦИИ: {e}")
        print("Проверьте правильность API ключей")
        return False
    except ccxt.NetworkError as e:
        print(f"✗ ОШИБКА СЕТИ: {e}")
        print("Проверьте подключение к интернету")
        return False
    except Exception as e:
        print(f"✗ НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    success = test_kucoin_connection()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
