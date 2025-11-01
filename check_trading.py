"""
ПРОВЕРКА НАСТРОЕК ТОРГОВЛИ
"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def check_trading_settings():
    """Проверка настроек торговли"""
    print("🔧 ПРОВЕРКА НАСТРОЕК ТОРГОВЛИ")
    print("=" * 50)
    
    # Проверяем API ключи
    api_key = os.getenv('KUCOIN_API_KEY')
    secret_key = os.getenv('KUCOIN_SECRET_KEY')
    passphrase = os.getenv('KUCOIN_PASSPHRASE')
    
    print(f"🔑 KUCOIN_API_KEY: {'✅ Установлен' if api_key else '❌ Отсутствует'}")
    print(f"🔑 KUCOIN_SECRET_KEY: {'✅ Установлен' if secret_key else '❌ Отсутствует'}")
    print(f"🔑 KUCOIN_PASSPHRASE: {'✅ Установлен' if passphrase else '❌ Отсутствует'}")
    
    if not all([api_key, secret_key, passphrase]):
        print("\n❌ API ключи KuCoin не настроены!")
        print("💡 Добавьте в файл .env:")
        print("KUCOIN_API_KEY=ваш_api_key")
        print("KUCOIN_SECRET_KEY=ваш_secret_key")
        print("KUCOIN_PASSPHRASE=ваш_passphrase")
        return False
    
    # Проверяем подключение к бирже
    try:
        from core.exchange import ExchangeManager
        exchange = ExchangeManager()
        
        if exchange.connected:
            print("✅ Подключение к KuCoin: УСПЕШНО")
            
            # Проверяем баланс
            balance = exchange.get_balance()
            if balance:
                print(f"💰 Баланс USDT: {balance['free_usdt']:.2f} свободно")
                print(f"💰 Баланс BTC: {balance['free_btc']:.6f} свободно")
                
                # Проверяем минимальный объем
                if balance['free_usdt'] < 0.1:
                    print("❌ НЕДОСТАТОЧНО СРЕДСТВ: Минимум 0.1 USDT требуется для торговли")
                    print("💡 Пополните баланс на KuCoin")
                    return False
                else:
                    print("✅ Баланс достаточен для торговли")
            else:
                print("❌ Не удалось получить баланс")
                return False
                
            # Проверяем информацию о рынке
            symbol = 'BTC/USDT'
            market_info = exchange.get_market_info(symbol)
            if market_info:
                print(f"📊 Информация о рынке {symbol}:")
                print(f"   Минимальное количество: {market_info['min_amount']}")
                print(f"   Минимальная сумма: {market_info['min_cost']} USDT")
                print(f"   Точность цены: {market_info['price_precision']}")
                print(f"   Точность количества: {market_info['amount_precision']}")
            else:
                print("❌ Не удалось получить информацию о рынке")
                
        else:
            print("❌ Подключение к KuCoin: НЕУДАЧНО")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки торговли: {e}")
        return False
    
    # Проверяем настройки бота
    try:
        from config.settings import SettingsManager
        settings = SettingsManager()
        
        print(f"\n⚙️ НАСТРОЙКИ БОТА:")
        print(f"   Режим торговли: {'🟢 ДЕМО' if settings.settings['demo_mode'] else '🔴 РЕАЛЬНЫЙ'}")
        print(f"   Размер позиции: {settings.settings['trade_amount_percent']*100:.1f}%")
        print(f"   Торговля включена: {'✅ ДА' if settings.settings['trading_enabled'] else '❌ НЕТ'}")
        
        # Расчет минимального размера позиции
        if balance:
            min_position_usdt = balance['free_usdt'] * settings.settings['trade_amount_percent']
            print(f"   Текущий размер ставки: {min_position_usdt:.2f} USDT")
            
            if min_position_usdt < 0.1:
                print("❌ РАЗМЕР СТАВКИ МАЛ: Увеличьте trade_amount_percent в настройках")
                recommended_percent = (0.1 / balance['free_usdt']) * 100
                print(f"💡 Рекомендуемый размер: {recommended_percent:.1f}%")
        
    except Exception as e:
        print(f"❌ Ошибка проверки настроек: {e}")
        return False
    
    print("\n✅ ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО")
    print("💡 Бот готов к работе!")
    return True

if __name__ == "__main__":
    check_trading_settings()