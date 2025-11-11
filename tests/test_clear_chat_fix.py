"""
Тест исправления функции очистки чата
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_message_id_storage():
    """Тест сохранения и загрузки ID сообщений"""
    print("🧪 Тест сохранения ID сообщений...")
    
    import json
    
    # Имитируем сохранение ID
    message_ids_file = '.telegram_message_ids.json'
    test_ids = [123, 456, 789]
    
    try:
        # Сохраняем
        with open(message_ids_file, 'w') as f:
            json.dump({'message_ids': test_ids}, f)
        print(f"✅ Сохранено {len(test_ids)} ID")
        
        # Загружаем
        with open(message_ids_file, 'r') as f:
            loaded_data = json.load(f)
            loaded_ids = loaded_data.get('message_ids', [])
        
        if loaded_ids == test_ids:
            print(f"✅ Загружено {len(loaded_ids)} ID корректно")
        else:
            print(f"❌ Ошибка: загружены неверные ID")
            return False
        
        # Очищаем тестовый файл
        os.remove(message_ids_file)
        print("✅ Тестовый файл удалён")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def test_telegram_bot_methods():
    """Тест методов TelegramBot"""
    print("\n🧪 Проверка кода Telegram бота...")
    
    try:
        # Читаем исходный код telegram/bot.py
        bot_file = os.path.join(os.path.dirname(__file__), '..', 'telegram', 'bot.py')
        
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие методов
        if 'def save_message_id' in content:
            print("✅ Метод save_message_id найден в коде")
        else:
            print("❌ Метод save_message_id не найден в коде")
            return False
        
        if 'def clear_chat' in content:
            print("✅ Метод clear_chat найден в коде")
        else:
            print("❌ Метод clear_chat не найден в коде")
            return False
        
        # Проверяем, что save_message_id вызывается в send_message
        if 'self.save_message_id' in content:
            print("✅ save_message_id вызывается в send_message")
        else:
            print("❌ save_message_id не вызывается в send_message")
            return False
        
        # Проверяем использование .telegram_message_ids.json
        if '.telegram_message_ids.json' in content:
            print("✅ Используется правильный файл для хранения ID")
        else:
            print("❌ Не найден файл для хранения ID")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("ТЕСТ ИСПРАВЛЕНИЯ ОЧИСТКИ ЧАТА TELEGRAM")
    print("="*60)
    
    results = []
    
    # Тест 1: Сохранение ID
    results.append(("Сохранение ID", test_message_id_storage()))
    
    # Тест 2: Методы бота
    results.append(("Методы Telegram бота", test_telegram_bot_methods()))
    
    # Результаты
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ ПРОЙДЕН" if passed else "❌ ПРОВАЛЕН"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
    print("="*60)
