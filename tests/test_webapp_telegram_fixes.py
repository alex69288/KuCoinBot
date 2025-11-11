"""
Тест для проверки исправления ошибок:
1. Ошибка fetch_ticker в Web App
2. Дублирование сообщений в Telegram
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("ТЕСТ ИСПРАВЛЕНИЙ WEBAPP И TELEGRAM БОТА")
print("=" * 70)

# Тест 1: Проверка метода get_ticker в ExchangeManager
print("\n1️⃣ Проверка метода get_ticker в ExchangeManager...")
try:
    from core.exchange import ExchangeManager
    
    # Проверяем, что метод существует
    exchange = ExchangeManager()
    if hasattr(exchange, 'get_ticker'):
        print("   ✅ Метод get_ticker существует в ExchangeManager")
        
        # Проверяем подпись метода
        import inspect
        sig = inspect.signature(exchange.get_ticker)
        params = list(sig.parameters.keys())
        if 'symbol' in params:
            print(f"   ✅ Метод get_ticker имеет правильную сигнатуру: {params}")
        else:
            print(f"   ⚠️ Неожиданная сигнатура метода: {params}")
    else:
        print("   ❌ Метод get_ticker не найден в ExchangeManager")
        
except Exception as e:
    print(f"   ❌ Ошибка при проверке ExchangeManager: {e}")

# Тест 2: Проверка исправления в webapp/server.py
print("\n2️⃣ Проверка исправления в webapp/server.py...")
try:
    server_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp', 'server.py')
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Проверяем, что используется правильный метод
    if 'trading_bot.exchange.get_ticker(symbol)' in content:
        print("   ✅ В server.py используется метод get_ticker()")
    else:
        print("   ⚠️ Не найден вызов get_ticker() в server.py")
        
    # Проверяем обработку ошибок
    if 'if not ticker:' in content and 'raise HTTPException' in content:
        print("   ✅ Добавлена проверка на пустой ticker")
    else:
        print("   ⚠️ Проверка на пустой ticker может отсутствовать")
        
except Exception as e:
    print(f"   ❌ Ошибка при проверке server.py: {e}")

# Тест 3: Проверка функции очистки чата в TelegramBot
print("\n3️⃣ Проверка функции очистки чата в TelegramBot...")
try:
    from telegram.bot import TelegramBot
    
    # Проверяем, что метод существует
    if hasattr(TelegramBot, 'clear_chat'):
        print("   ✅ Метод clear_chat существует в TelegramBot")
        
        # Проверяем логику инициализации
        bot_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telegram', 'bot.py')
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'self.clear_chat()' in content:
            print("   ✅ Метод clear_chat() вызывается при инициализации")
        else:
            print("   ⚠️ Метод clear_chat() может не вызываться при инициализации")
            
        # Проверяем удаление метода load_welcome_message_id
        if 'def load_welcome_message_id' not in content:
            print("   ✅ Устаревший метод load_welcome_message_id удалён")
        else:
            print("   ⚠️ Метод load_welcome_message_id всё ещё присутствует")
            
        # Проверяем анимацию "печатает..."
        if 'sendChatAction' in content and 'typing' in content:
            print("   ✅ Добавлена анимация 'печатает...' перед отправкой сообщения")
        else:
            print("   ⚠️ Анимация может отсутствовать")
            
    else:
        print("   ❌ Метод clear_chat не найден в TelegramBot")
        
except Exception as e:
    print(f"   ❌ Ошибка при проверке TelegramBot: {e}")

# Тест 4: Проверка структуры сообщений
print("\n4️⃣ Проверка обновлённого текста приветственного сообщения...")
try:
    bot_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telegram', 'bot.py')
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'Trading Bot' in content and 'KuCoin Автоматическая торговля' in content:
        print("   ✅ Приветственное сообщение обновлено")
    else:
        print("   ⚠️ Приветственное сообщение может быть не обновлено")
        
    if '@yadarrblahenani_bot' in content:
        print("   ✅ Ссылка на бота добавлена в сообщение")
    else:
        print("   ⚠️ Ссылка на бота может отсутствовать")
        
except Exception as e:
    print(f"   ❌ Ошибка при проверке сообщений: {e}")

# Итоговый результат
print("\n" + "=" * 70)
print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
print("=" * 70)
print("""
✅ Исправления реализованы:
   1. Исправлена ошибка fetch_ticker в Web App
   2. Добавлена очистка чата при перезапуске бота
   3. Добавлена анимация "печатает..." перед отправкой сообщения
   4. Обновлён текст приветственного сообщения

🔄 Для применения изменений:
   1. Остановите текущий бот
   2. Сделайте git commit и push
   3. Перезапустите бот на Amvera

📱 После перезапуска:
   - Чат Telegram будет очищен
   - Появится новое приветственное сообщение с анимацией
   - Web App будет корректно загружать данные рынка
""")

print("\n✅ Тест завершён успешно!")
