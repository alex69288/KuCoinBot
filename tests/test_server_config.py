"""
Тест конфигурации бота на сервере
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    env_file = root_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Загружен .env файл: {env_file}")
except ImportError:
    print("Предупреждение: python-dotenv не установлен")

def check_environment():
    """Проверка переменных окружения"""
    print("=" * 50)
    print("Проверка переменных окружения")
    print("=" * 50)
    
    required_vars = [
        'KUCOIN_API_KEY',
        'KUCOIN_SECRET_KEY',
        'KUCOIN_PASSPHRASE',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Маскируем значение для безопасности
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: НЕ УСТАНОВЛЕНА")
            missing.append(var)
    
    print()
    if missing:
        print(f"ОШИБКА: Отсутствуют переменные: {', '.join(missing)}")
        return False
    else:
        print("✓ Все переменные окружения установлены")
        return True

def check_imports():
    """Проверка импорта модулей"""
    print("\n" + "=" * 50)
    print("Проверка импорта модулей")
    print("=" * 50)
    
    modules = [
        ('ccxt', 'CCXT (биржевой API)'),
        ('telegram', 'Python Telegram Bot'),
        ('fastapi', 'FastAPI'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),
        ('aiohttp', 'AIOHTTP'),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✓ {description}: OK")
        except ImportError as e:
            print(f"✗ {description}: ОШИБКА - {e}")
            all_ok = False
    
    print()
    if all_ok:
        print("✓ Все модули импортированы успешно")
    else:
        print("ОШИБКА: Некоторые модули не установлены")
    
    return all_ok

def check_project_structure():
    """Проверка структуры проекта"""
    print("\n" + "=" * 50)
    print("Проверка структуры проекта")
    print("=" * 50)
    
    required_dirs = [
        'config',
        'core',
        'strategies',
        'telegram',
        'utils',
        'webapp',
        'ml',
        'analytics'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            print(f"✓ Директория {dir_name}: OK")
        else:
            print(f"✗ Директория {dir_name}: НЕ НАЙДЕНА")
            all_ok = False
    
    print()
    if all_ok:
        print("✓ Структура проекта в порядке")
    else:
        print("ОШИБКА: Отсутствуют некоторые директории")
    
    return all_ok

def main():
    """Главная функция проверки"""
    print("\n" + "=" * 50)
    print("ПРОВЕРКА КОНФИГУРАЦИИ БОТА")
    print("=" * 50)
    print(f"Python версия: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    print(f"Корневая директория проекта: {root_dir}")
    print()
    
    results = []
    results.append(("Переменные окружения", check_environment()))
    results.append(("Импорт модулей", check_imports()))
    results.append(("Структура проекта", check_project_structure()))
    
    print("\n" + "=" * 50)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("Бот готов к запуску.")
        return 0
    else:
        print("✗ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print("Необходимо устранить ошибки перед запуском.")
        return 1

if __name__ == "__main__":
    exit(main())
