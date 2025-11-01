"""
ДЕБАГ ТОРГОВОЙ ЛОГИКИ
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_trading_logic():
    """Диагностика торговой логики"""
    from core.bot import AdvancedTradingBot
    from utils.logger import log_info
    
    print("🔧 ДИАГНОСТИКА ТОРГОВОЙ ЛОГИКИ")
    print("=" * 50)
    
    bot = AdvancedTradingBot()
    
    # Принудительно сбрасываем состояние для теста
    bot.position = None
    bot.last_signal = None
    bot.entry_price = 0
    bot.current_position_size_usdt = 0
    bot.last_trade_time = 0
    
    print("🤖 Состояние бота сброшено для тестирования")
    print(f"📊 Позиция: {bot.position}")
    print(f"📊 Last signal: {bot.last_signal}")
    print(f"💰 Entry price: {bot.entry_price}")
    print(f"⏰ Last trade time: {bot.last_trade_time}")
    
    # Запускаем один цикл торговли
    print("\n🚀 Запускаем тестовый торговый цикл...")
    bot.execute_trading_cycle()
    
    print("\n📊 Результат:")
    print(f"📊 Позиция: {bot.position}")
    print(f"📊 Last signal: {bot.last_signal}")
    print(f"💰 Entry price: {bot.entry_price}")
    print(f"⏰ Last trade time: {bot.last_trade_time}")

def force_buy_signal():
    """Принудительное создание условий для покупки"""
    from core.bot import AdvancedTradingBot
    from utils.logger import log_info
    
    print("🟢 ПРИНУДИТЕЛЬНАЯ ПОКУПКА")
    print("=" * 50)
    
    bot = AdvancedTradingBot()
    
    # Сбрасываем состояние
    bot.position = None
    bot.last_signal = None
    bot.entry_price = 0
    bot.current_position_size_usdt = 0
    bot.last_trade_time = 0
    
    # Получаем рыночные данные
    symbol = bot.settings.trading_pairs['active_pair']
    market_data = bot.exchange.get_market_data(symbol)
    
    if market_data:
        # Имитируем идеальные условия для покупки
        market_data['ema_diff_percent'] = 0.01  # Сильный восходящий тренд
        
        print(f"📊 Созданы идеальные условия:")
        print(f"   Цена: {market_data['current_price']:.2f}")
        print(f"   EMA diff: {market_data['ema_diff_percent']:.4f}")
        print(f"   Позиция: {bot.position}")
        
        # Запускаем цикл
        bot.execute_trading_cycle()
        
        print(f"\n📊 Результат:")
        print(f"   Позиция: {bot.position}")
        print(f"   Last signal: {bot.last_signal}")
        
        if bot.position == 'long':
            print("✅ ПОКУПКА ВЫПОЛНЕНА УСПЕШНО!")
        else:
            print("❌ ПОКУПКА НЕ ВЫПОЛНЕНА")

if __name__ == "__main__":
    debug_trading_logic()
    print("\n" + "="*50)
    force_buy_signal()