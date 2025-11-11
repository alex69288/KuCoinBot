#!/usr/bin/env python3
"""
Комплексная проверка готовности бота к запуску на сервере
"""
import os
import sys
import subprocess
from pathlib import Path

# Цвета для терминала
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def colored(text, color):
    """Возвращает цветной текст"""
    return f"{color}{text}{RESET}"

def run_test(test_name, test_path):
    """Запускает тест и возвращает результат"""
    print(f"\n{colored('▶', BLUE)} Запуск теста: {test_name}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print(colored(result.stderr, YELLOW))
        
        if result.returncode == 0:
            print(colored(f"✓ {test_name}: PASS", GREEN))
            return True
        else:
            print(colored(f"✗ {test_name}: FAIL", RED))
            return False
            
    except subprocess.TimeoutExpired:
        print(colored(f"✗ {test_name}: TIMEOUT", RED))
        return False
    except Exception as e:
        print(colored(f"✗ {test_name}: ERROR - {e}", RED))
        return False

def main():
    """Главная функция проверки"""
    print(colored("\n" + "=" * 60, BLUE))
    print(colored("КОМПЛЕКСНАЯ ПРОВЕРКА ГОТОВНОСТИ БОТА", BLUE))
    print(colored("=" * 60 + "\n", BLUE))
    
    # Определяем корневую директорию
    if os.path.exists('/home/botuser/KuCoinBot'):
        root_dir = Path('/home/botuser/KuCoinBot')
        print(f"Режим: {colored('СЕРВЕР', YELLOW)}")
    else:
        root_dir = Path(__file__).parent.parent
        print(f"Режим: {colored('ЛОКАЛЬНЫЙ', YELLOW)}")
    
    print(f"Корневая директория: {root_dir}")
    print()
    
    tests_dir = root_dir / 'tests'
    
    # Список тестов для запуска
    tests = [
        ("Конфигурация сервера", tests_dir / "test_server_config.py"),
        ("Подключение к KuCoin API", tests_dir / "test_kucoin_api.py"),
    ]
    
    results = []
    
    # Запускаем каждый тест
    for test_name, test_path in tests:
        if not test_path.exists():
            print(colored(f"⚠ Тест '{test_name}' не найден: {test_path}", YELLOW))
            results.append((test_name, False))
            continue
        
        success = run_test(test_name, test_path)
        results.append((test_name, success))
    
    # Итоговый отчет
    print(colored("\n" + "=" * 60, BLUE))
    print(colored("ИТОГОВЫЙ ОТЧЕТ", BLUE))
    print(colored("=" * 60, BLUE))
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        if success:
            print(colored(f"✓ {test_name}", GREEN))
            passed += 1
        else:
            print(colored(f"✗ {test_name}", RED))
            failed += 1
    
    print()
    print(f"Всего тестов: {len(results)}")
    print(colored(f"Пройдено: {passed}", GREEN))
    if failed > 0:
        print(colored(f"Провалено: {failed}", RED))
    
    print()
    
    if failed == 0:
        print(colored("=" * 60, GREEN))
        print(colored("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!", GREEN))
        print(colored("Бот готов к запуску на сервере.", GREEN))
        print(colored("=" * 60, GREEN))
        print()
        print("Для запуска бота выполните:")
        print(colored("  cd /home/botuser/KuCoinBot", YELLOW))
        print(colored("  source venv/bin/activate", YELLOW))
        print(colored("  python main.py", YELLOW))
        return 0
    else:
        print(colored("=" * 60, RED))
        print(colored("✗ ОБНАРУЖЕНЫ ПРОБЛЕМЫ", RED))
        print(colored("Устраните ошибки перед запуском бота.", RED))
        print(colored("=" * 60, RED))
        return 1

if __name__ == "__main__":
    exit(main())
