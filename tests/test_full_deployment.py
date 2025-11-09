"""
Полный тест деплоя на Amvera
Проверяет все компоненты системы
"""
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all_files_exist():
    """Проверяем наличие всех критичных файлов"""
    print("\n📋 Проверка наличия файлов...")
    
    required_files = [
        'amvera.yml',
        'requirements.txt',
        'start.py',
        'check_env.py',
        'main_with_webapp.py',
        'main.py',
        'ENVIRONMENT_SETUP.md',
        'DEPLOYMENT_STATUS.md',
    ]
    
    missing_files = []
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    for file in required_files:
        file_path = os.path.join(root_dir, file)
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - НЕ НАЙДЕН")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_amvera_yml_structure():
    """Проверяем структуру amvera.yml"""
    print("\n📋 Проверка amvera.yml...")
    
    amvera_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'amvera.yml')
    
    with open(amvera_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('meta:', 'секция meta'),
        ('environment: python', 'тип окружения python'),
        ('name: pip', 'менеджер пакетов pip'),
        ('version: 3.11', 'версия Python 3.11'),
        ('build:', 'секция build'),
        ('requirementsPath: requirements.txt', 'путь к requirements'),
        ('run:', 'секция run'),
        ('scriptName: start.py', 'скрипт запуска start.py'),
        ('containerPort: 8000', 'порт контейнера 8000'),
        ('persistenceMount: /data', 'персистентное хранилище'),
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - НЕ НАЙДЕНО")
            all_passed = False
    
    return all_passed

def test_requirements_content():
    """Проверяем содержимое requirements.txt"""
    print("\n📋 Проверка requirements.txt...")
    
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    required_packages = [
        'ccxt',
        'python-dotenv',
        'requests',
        'pandas',
        'fastapi',
        'uvicorn',
        'python-telegram-bot',
    ]
    
    all_found = True
    for package in required_packages:
        if package in content:
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} - НЕ НАЙДЕН")
            all_found = False
    
    return all_found

def test_start_py_logic():
    """Проверяем логику start.py"""
    print("\n📋 Проверка логики start.py...")
    
    start_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'start.py')
    
    with open(start_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('from check_env import check_environment', 'импорт функции проверки'),
        ('from main_with_webapp import main', 'импорт основного приложения'),
        ('if not check_environment():', 'проверка окружения'),
        ('return 1', 'возврат ошибки при отсутствии переменных'),
        ('app_main()', 'запуск приложения'),
        ('if __name__ == "__main__":', 'точка входа'),
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - НЕ НАЙДЕНО")
            all_passed = False
    
    return all_passed

def test_check_env_logic():
    """Проверяем логику check_env.py"""
    print("\n📋 Проверка логики check_env.py...")
    
    check_env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'check_env.py')
    
    with open(check_env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_vars = [
        'KUCOIN_API_KEY',
        'KUCOIN_SECRET_KEY',
        'KUCOIN_PASSPHRASE',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
    ]
    
    all_found = True
    for var in required_vars:
        if var in content:
            print(f"   ✅ {var}")
        else:
            print(f"   ❌ {var} - НЕ ПРОВЕРЯЕТСЯ")
            all_found = False
    
    return all_found

def test_port_configuration():
    """Проверяем конфигурацию портов"""
    print("\n📋 Проверка конфигурации портов...")
    
    # Проверяем amvera.yml
    amvera_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'amvera.yml')
    with open(amvera_file, 'r', encoding='utf-8') as f:
        amvera_content = f.read()
    
    # Проверяем main_with_webapp.py
    main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main_with_webapp.py')
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    checks_passed = True
    
    if 'containerPort: 8000' in amvera_content:
        print("   ✅ amvera.yml использует порт 8000")
    else:
        print("   ❌ amvera.yml не использует порт 8000")
        checks_passed = False
    
    if "PORT = int(os.getenv('PORT', 8000))" in main_content or "PORT', 8000)" in main_content:
        print("   ✅ main_with_webapp.py использует порт 8000 по умолчанию")
    else:
        print("   ⚠️  Проверьте конфигурацию порта в main_with_webapp.py")
    
    return checks_passed

def test_documentation():
    """Проверяем наличие документации"""
    print("\n📋 Проверка документации...")
    
    docs = {
        'ENVIRONMENT_SETUP.md': 'инструкция по настройке переменных окружения',
        'DEPLOYMENT_STATUS.md': 'статус деплоя и быстрый старт',
        'README.md': 'основная документация проекта',
    }
    
    all_found = True
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    for doc_file, description in docs.items():
        file_path = os.path.join(root_dir, doc_file)
        if os.path.exists(file_path):
            print(f"   ✅ {doc_file} - {description}")
        else:
            print(f"   ❌ {doc_file} - НЕ НАЙДЕН")
            all_found = False
    
    return all_found

def main():
    """Запуск всех тестов"""
    print("=" * 70)
    print("🚀 ПОЛНЫЙ ТЕСТ СИСТЕМЫ ДЕПЛОЯ НА AMVERA")
    print("=" * 70)
    
    tests = [
        ("Наличие критичных файлов", test_all_files_exist),
        ("Структура amvera.yml", test_amvera_yml_structure),
        ("Зависимости в requirements.txt", test_requirements_content),
        ("Логика start.py", test_start_py_logic),
        ("Валидация окружения check_env.py", test_check_env_logic),
        ("Конфигурация портов", test_port_configuration),
        ("Документация", test_documentation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 70}")
        print(f"🧪 Тест: {test_name}")
        print('=' * 70)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Итоги
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status:15} | {test_name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Пройдено: {passed}/{len(results)}")
    print(f"❌ Провалено: {failed}/{len(results)}")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ГОТОВА К ДЕПЛОЮ!")
        print("\n📝 Следующие шаги:")
        print("   1. Убедитесь что все изменения залиты в GitHub")
        print("   2. Перезапустите приложение в Amvera")
        print("   3. Настройте переменные окружения (см. ENVIRONMENT_SETUP.md)")
        print("   4. Проверьте логи - должно быть '✅ Переменные окружения настроены'")
        print("   5. Проверьте работу бота через Telegram")
        print("=" * 70)
        return 0
    else:
        print(f"\n⚠️ ВНИМАНИЕ: {failed} тест(ов) провалено")
        print("   Исправьте ошибки перед деплоем!")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
