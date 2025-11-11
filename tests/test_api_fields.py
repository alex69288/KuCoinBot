"""
Тест для проверки соответствия полей API и frontend
"""
import json
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def test_api_field_names():
    """Проверяем, что API возвращает правильные названия полей"""
    
    # Проверяем server.py
    server_file = root_dir / 'webapp' / 'server.py'
    if not server_file.exists():
        print("❌ Файл webapp/server.py не найден")
        return False
    
    server_content = server_file.read_text(encoding='utf-8')
    
    # Проверяем /api/status
    required_status_fields = [
        'trading_enabled',  # Не is_running!
        'balance',
        'position',
        'pnl'
    ]
    
    print("\n🔍 Проверка /api/status:")
    for field in required_status_fields:
        if f'"{field}":' in server_content or f'"{field}"' in server_content:
            print(f"  ✅ Поле '{field}' найдено")
        else:
            print(f"  ❌ Поле '{field}' НЕ найдено")
            return False
    
    # Проверяем /api/market
    print("\n🔍 Проверка /api/market:")
    if '"change_24h":' in server_content or '"change_24h"' in server_content:
        print("  ✅ Поле 'change_24h' найдено")
    else:
        print("  ❌ Поле 'change_24h' НЕ найдено (возможно используется price_change_24h)")
        return False
    
    # Проверяем, что старые поля удалены
    print("\n🔍 Проверка устаревших полей:")
    if '"is_running":' in server_content:
        print("  ⚠️  Найдено устаревшее поле 'is_running' (должно быть trading_enabled)")
        return False
    else:
        print("  ✅ Устаревшее поле 'is_running' не найдено")
    
    if '"price_change_24h":' in server_content:
        print("  ⚠️  Найдено устаревшее поле 'price_change_24h' (должно быть change_24h)")
        return False
    else:
        print("  ✅ Устаревшее поле 'price_change_24h' не найдено")
    
    return True


def test_frontend_expects_correct_fields():
    """Проверяем, что frontend ожидает правильные поля"""
    
    index_file = root_dir / 'webapp' / 'static' / 'index.html'
    if not index_file.exists():
        print("❌ Файл webapp/static/index.html не найден")
        return False
    
    index_content = index_file.read_text(encoding='utf-8')
    
    print("\n🔍 Проверка frontend (index.html):")
    
    # Проверяем правильные поля
    correct_fields = {
        'trading_enabled': 'data.trading_enabled',
        'balance': 'data.balance',
        'position': 'data.position',
        'pnl': 'data.pnl',
        'change_24h': 'data.change_24h'
    }
    
    for field_name, field_access in correct_fields.items():
        if field_access in index_content:
            print(f"  ✅ Frontend использует '{field_access}'")
        else:
            print(f"  ❌ Frontend НЕ использует '{field_access}'")
            return False
    
    # Проверяем, что нет обращений к старым полям
    print("\n🔍 Проверка отсутствия устаревших обращений:")
    
    if 'data.is_running' in index_content:
        print("  ⚠️  Frontend обращается к устаревшему 'data.is_running'")
        return False
    else:
        print("  ✅ Нет обращений к устаревшему 'data.is_running'")
    
    if 'data.price_change_24h' in index_content:
        print("  ⚠️  Frontend обращается к устаревшему 'data.price_change_24h'")
        return False
    else:
        print("  ✅ Нет обращений к устаревшему 'data.price_change_24h'")
    
    return True


def test_balance_handling():
    """Проверяем обработку balance (может быть number или object)"""
    
    index_file = root_dir / 'webapp' / 'static' / 'index.html'
    index_content = index_file.read_text(encoding='utf-8')
    
    print("\n🔍 Проверка обработки balance:")
    
    # Проверяем наличие защитного кода для balance
    balance_checks = [
        'typeof data.balance',
        'data.balance?.total_usdt'
    ]
    
    all_found = all(check in index_content for check in balance_checks)
    
    if all_found:
        print("  ✅ Balance обрабатывается корректно (поддержка number и object)")
    else:
        print("  ⚠️  Обработка balance может быть неполной")
        return False
    
    return True


def main():
    """Запускаем все тесты"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ СООТВЕТСТВИЯ API И FRONTEND")
    print("=" * 60)
    
    tests = [
        ("API поля", test_api_field_names),
        ("Frontend ожидания", test_frontend_expects_correct_fields),
        ("Обработка balance", test_balance_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Тест: {test_name}")
        print('=' * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка при выполнении теста: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("API и frontend используют согласованные названия полей")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Требуется исправление несоответствий")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
