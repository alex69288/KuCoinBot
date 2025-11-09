"""
Тест проверки start.py и валидации окружения
"""
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_start_file_exists():
    """Проверяем, что start.py существует"""
    start_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'start.py')
    assert os.path.exists(start_file), "Файл start.py не найден"
    print("✅ Файл start.py существует")

def test_check_env_exists():
    """Проверяем, что check_env.py существует"""
    check_env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'check_env.py')
    assert os.path.exists(check_env_file), "Файл check_env.py не найден"
    print("✅ Файл check_env.py существует")

def test_check_env_import():
    """Проверяем, что можно импортировать check_environment"""
    try:
        from check_env import check_environment
        print("✅ Функция check_environment импортируется корректно")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_check_env_without_vars():
    """Проверяем, что check_environment возвращает False без переменных"""
    # Сохраняем текущие переменные
    saved_vars = {}
    required_vars = [
        'KUCOIN_API_KEY',
        'KUCOIN_API_SECRET', 
        'KUCOIN_API_PASSPHRASE',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    for var in required_vars:
        saved_vars[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        from check_env import check_environment
        result = check_environment()
        
        # Восстанавливаем переменные
        for var, value in saved_vars.items():
            if value is not None:
                os.environ[var] = value
        
        if result:
            print("❌ check_environment должна возвращать False без переменных")
            return False
        else:
            print("✅ check_environment корректно возвращает False без переменных")
            return True
    except Exception as e:
        # Восстанавливаем переменные в случае ошибки
        for var, value in saved_vars.items():
            if value is not None:
                os.environ[var] = value
        print(f"❌ Ошибка теста: {e}")
        return False

def test_start_py_structure():
    """Проверяем структуру start.py"""
    start_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'start.py')
    
    with open(start_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('check_environment', 'импорт check_environment'),
        ('main_with_webapp', 'импорт main_with_webapp'),
        ('def main()', 'определение функции main'),
        ('if __name__', 'точка входа'),
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description} найден")
        else:
            print(f"❌ {description} не найден")
            all_passed = False
    
    return all_passed

def test_amvera_yml_updated():
    """Проверяем, что amvera.yml обновлен на start.py"""
    amvera_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'amvera.yml')
    
    with open(amvera_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'scriptName: start.py' in content:
        print("✅ amvera.yml настроен на start.py")
        return True
    else:
        print("❌ amvera.yml не использует start.py")
        return False

def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ЗАПУСКА")
    print("=" * 60)
    
    tests = [
        ("Существование start.py", test_start_file_exists),
        ("Существование check_env.py", test_check_env_exists),
        ("Импорт check_environment", test_check_env_import),
        ("Валидация без переменных", test_check_env_without_vars),
        ("Структура start.py", test_start_py_structure),
        ("Обновление amvera.yml", test_amvera_yml_updated),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Тест: {test_name}")
        print("-" * 60)
        try:
            result = test_func()
            if result is None or result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Всего: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print(f"\n⚠️  ЕСТЬ ПРОБЛЕМЫ: {failed} тест(ов) провалено")
        return 1

if __name__ == "__main__":
    sys.exit(main())
