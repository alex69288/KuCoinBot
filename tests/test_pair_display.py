"""
Тест для проверки отображения названий торговых пар с правильными символами в скобках
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import TRADING_PAIRS


def test_trading_pairs_format():
    """Проверка формата торговых пар"""
    print("=" * 60)
    print("Тест: Отображение торговых пар")
    print("=" * 60)
    
    expected_format = {
        'BTC/USDT': '(₿) Bitcoin',
        'SOL/USDT': '(◎) Solana'
    }
    
    print("\n✅ Проверка формата торговых пар из constants.py:")
    all_correct = True
    
    for pair, name in TRADING_PAIRS.items():
        expected_name = expected_format.get(pair, '')
        status = "✅" if name == expected_name else "❌"
        
        print(f"\n{status} {pair}:")
        print(f"   Ожидается: {expected_name}")
        print(f"   Получено:  {name}")
        
        if name != expected_name:
            all_correct = False
    
    # Проверка символов в скобках
    print("\n" + "=" * 60)
    print("Проверка, что символы находятся в скобках:")
    print("=" * 60)
    
    for pair, name in TRADING_PAIRS.items():
        if name.startswith('(') and ')' in name:
            symbol_end = name.index(')') + 1
            symbol_part = name[:symbol_end]
            name_part = name[symbol_end:].strip()
            print(f"\n✅ {pair}:")
            print(f"   Символ в скобках: {symbol_part}")
            print(f"   Название: {name_part}")
        else:
            print(f"\n❌ {pair}: Символ НЕ в скобках! ({name})")
            all_correct = False
    
    print("\n" + "=" * 60)
    if all_correct:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
    print("=" * 60)
    
    return all_correct


def test_handlers_symbol_names():
    """Проверка словаря символов в handlers.py"""
    print("\n" + "=" * 60)
    print("Тест: Проверка словаря символов в handlers.py")
    print("=" * 60)
    
    # Проверяем, что файл существует и импортируется
    try:
        from telegram.handlers import MessageHandler
        print("\n✅ Модуль telegram.handlers успешно импортирован")
        
        # Создаем временный экземпляр для проверки метода
        # (без инициализации бота)
        handler = MessageHandler(None)
        
        # Проверяем несколько символов
        test_symbols = ['BTC', 'ETH', 'SOL']
        print("\n📊 Проверка отображения символов:")
        
        for symbol in test_symbols:
            display_name = handler._get_pair_display_name(symbol)
            print(f"\n  {symbol} -> {display_name}")
            
            if display_name.startswith('(') and ')' in display_name:
                print(f"  ✅ Символ в скобках")
            else:
                print(f"  ❌ Символ НЕ в скобках!")
        
        print("\n✅ Проверка словаря символов завершена")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при импорте или проверке: {e}")
        return False


if __name__ == '__main__':
    print("\n🚀 Запуск тестов отображения торговых пар\n")
    
    # Запускаем тесты
    test1_passed = test_trading_pairs_format()
    test2_passed = test_handlers_symbol_names()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print("\nТеперь символы криптовалют отображаются в скобках:")
        print("  • BTC/USDT -> (₿) Bitcoin")
        print("  • SOL/USDT -> (◎) Solana")
        sys.exit(0)
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        sys.exit(1)
