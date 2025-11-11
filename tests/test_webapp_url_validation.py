"""
Тест для проверки исправления WebApp кнопки
Проверяет логику валидации URL без отправки в Telegram
"""
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_webapp_url_validation():
    """Тест валидации WEBAPP_URL"""
    
    print("\n" + "="*60)
    print("🧪 ТЕСТ ВАЛИДАЦИИ WEBAPP_URL")
    print("="*60 + "\n")
    
    test_cases = [
        # (URL, should_be_valid, description)
        ("", False, "Пустой URL"),
        ("https://your-server.com", False, "URL по умолчанию"),
        ("http://localhost:8080", False, "HTTP localhost"),
        ("http://127.0.0.1:8080", False, "HTTP IP адрес"),
        ("https://abc123.ngrok.io", True, "Ngrok HTTPS URL"),
        ("https://myapp.amvera.app", True, "Amvera HTTPS URL"),
        ("https://myapp.railway.app", True, "Railway HTTPS URL"),
        ("ftp://example.com", False, "Неправильный протокол"),
    ]
    
    passed = 0
    failed = 0
    
    for url, should_be_valid, description in test_cases:
        # Логика валидации из telegram/bot.py
        is_valid = False
        
        if url and url != 'https://your-server.com':
            if url.startswith('https://'):
                is_valid = True
        
        # Проверяем результат
        if is_valid == should_be_valid:
            print(f"✅ PASS: {description}")
            print(f"   URL: {url}")
            print(f"   Ожидалось: {'валидный' if should_be_valid else 'невалидный'}")
            print(f"   Результат: {'валидный' if is_valid else 'невалидный'}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   URL: {url}")
            print(f"   Ожидалось: {'валидный' if should_be_valid else 'невалидный'}")
            print(f"   Результат: {'валидный' if is_valid else 'невалидный'}")
            failed += 1
        print()
    
    print("="*60)
    print(f"📊 РЕЗУЛЬТАТЫ: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


def test_current_env():
    """Проверка текущей конфигурации .env"""
    
    print("\n" + "="*60)
    print("🔍 ПРОВЕРКА ТЕКУЩЕЙ КОНФИГУРАЦИИ")
    print("="*60 + "\n")
    
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.env'
    )
    
    if not os.path.exists(env_path):
        print("⚠️  Файл .env не найден")
        print("📝 Создайте .env файл и добавьте:")
        print("   WEBAPP_URL=https://ваш-url.ngrok.io")
        print()
        return False
    
    # Читаем .env
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие WEBAPP_URL
    webapp_url = None
    for line in content.split('\n'):
        if line.strip().startswith('WEBAPP_URL='):
            webapp_url = line.split('=', 1)[1].strip()
            break
    
    if not webapp_url:
        print("⚠️  WEBAPP_URL не установлена в .env")
        print("📝 Добавьте в .env файл:")
        print("   WEBAPP_URL=https://ваш-url.ngrok.io")
        print()
        return False
    
    print(f"✅ WEBAPP_URL найдена: {webapp_url}")
    
    # Валидация
    is_valid = False
    reason = ""
    
    if not webapp_url or webapp_url == 'https://your-server.com':
        reason = "URL не установлен или используется заглушка"
    elif not webapp_url.startswith('https://'):
        reason = "URL должен начинаться с https://"
    else:
        is_valid = True
        reason = "URL корректен"
    
    if is_valid:
        print(f"✅ Валидация: {reason}")
        print("\n💡 Бот будет отправлять кнопку WebApp")
    else:
        print(f"❌ Валидация: {reason}")
        print("\n💡 Бот покажет предупреждение вместо кнопки WebApp")
        print("\n📚 Инструкция по настройке: docs/WEBAPP_SETUP.md")
    
    print()
    return is_valid


def main():
    """Запуск всех тестов"""
    print("\n" + "🤖 ТЕСТ ИСПРАВЛЕНИЯ WEBAPP КНОПКИ" + "\n")
    
    # Тест 1: Валидация URL
    test1_passed = test_webapp_url_validation()
    
    # Тест 2: Текущая конфигурация
    test2_passed = test_current_env()
    
    # Итоги
    print("\n" + "="*60)
    print("📋 ИТОГИ")
    print("="*60)
    print(f"Тест валидации URL: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Проверка .env: {'✅ PASS' if test2_passed else '⚠️  ТРЕБУЕТ НАСТРОЙКИ'}")
    print()
    
    if not test2_passed:
        print("📖 ДЛЯ НАСТРОЙКИ WEBAPP:")
        print("   1. Прочитайте docs/WEBAPP_SETUP.md")
        print("   2. Выберите вариант развертывания (Ngrok/Amvera/Railway)")
        print("   3. Обновите WEBAPP_URL в .env файле")
        print()
        print("💡 БЕЗ WEBAPP:")
        print("   Бот полностью работает через команды Telegram")
        print("   WebApp - это дополнительный интерфейс")
        print()
    else:
        print("✅ Все готово! Бот будет корректно работать с WebApp")
        print()
    
    return test1_passed and test2_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
