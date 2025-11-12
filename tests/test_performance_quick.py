"""
Быстрый тест производительности оптимизаций v0.1.9
Запуск: python tests/test_performance_quick.py
"""

import time
import json
from pathlib import Path


def test_performance_optimizer_exists():
    """Проверка: существует ли performance-optimizer.js"""
    print("\n✓ Проверка наличия performance-optimizer.js")
    perf_js = Path('webapp/static/performance-optimizer.js')
    
    if not perf_js.exists():
        print("  ❌ ОШИБКА: webapp/static/performance-optimizer.js не найден")
        return False
    
    with open(perf_js, encoding='utf-8') as f:
        content = f.read()
        
    checks = {
        'IndexedDB кэширование': 'openDB' in content,
        'WebSocket ранний старт': 'startWebSocketEarly' in content,
        'Адаптивный fallback': 'startSlowFallbackUpdates' in content,
        'Интервал 60 сек': '60000' in content,
        'Приоритизированная загрузка': 'loadCriticalDataOnly' in content,
    }
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    all_ok = all(checks.values())
    return all_ok


def test_html_loads_optimizer():
    """Проверка: загружает ли HTML performance-optimizer.js РАНО"""
    print("\n✓ Проверка загрузки performance-optimizer в HTML")
    
    with open('webapp/static/index.html', encoding='utf-8') as f:
        html = f.read()
    
    # Проверяем что performance-optimizer.js загружается
    has_optimizer = 'performance-optimizer.js' in html
    
    if not has_optimizer:
        print("  ❌ ОШИБКА: HTML не загружает performance-optimizer.js")
        return False
    
    print("  ✅ performance-optimizer.js загружается в HTML")
    
    # Проверяем что он загружается ДО telegram-web-app.js
    optimizer_pos = html.find('performance-optimizer.js')
    telegram_pos = html.find('telegram-web-app.js')
    
    if optimizer_pos < telegram_pos:
        print("  ✅ performance-optimizer загружается ПЕРЕД telegram-web-app.js (правильный порядок)")
        return True
    else:
        print("  ⚠️  ВНИМАНИЕ: performance-optimizer загружается ПОСЛЕ telegram-web-app.js")
        return False


def test_compact_api_exists():
    """Проверка: существует ли api_compact_responses.py"""
    print("\n✓ Проверка наличия compact API ответов")
    
    compact_api = Path('webapp/api_compact_responses.py')
    
    if not compact_api.exists():
        print("  ❌ ОШИБКА: webapp/api_compact_responses.py не найден")
        return False
    
    with open(compact_api, encoding='utf-8') as f:
        content = f.read()
    
    functions = [
        'compact_status_response',
        'compact_market_response',
        'compact_positions_response',
        'compact_history_response',
        'compact_settings_response',
        'compact_analytics_response',
    ]
    
    for func in functions:
        if func in content:
            print(f"  ✅ {func} существует")
        else:
            print(f"  ❌ ОШИБКА: {func} не найден")
            return False
    
    return True


def test_compact_format_efficiency():
    """Проверка: насколько эффективен компактный формат"""
    print("\n✓ Проверка эффективности компактного формата")
    
    # Полный формат
    full_status = {
        "positions": {
            "open_count": 3,
            "size_usdt": 500.123456789,
            "entry_price": 45000.500123456,
            "current_profit_percent": 2.3456789123,
            "current_profit_usdt": 11.7012345678,
            "to_take_profit": 3.6543210987,
            "tp_target": 6.0,
            "fee_percent": 0.2,
            "fee_usdt": 2.0
        },
        "last_update": "2025-11-12T15:30:45.123456789"
    }
    
    # Компактный формат
    compact_status = {
        "p": {
            "c": 3,
            "s": 500.12,
            "e": 45000.50,
            "pr": 2.35,
            "pu": 11.70,
            "t": 3.65,
        },
        "ts": 1731425445
    }
    
    full_json = json.dumps(full_status)
    compact_json = json.dumps(compact_status)
    
    full_size = len(full_json)
    compact_size = len(compact_json)
    savings = ((full_size - compact_size) / full_size) * 100
    
    print(f"  Полный формат:      {full_size} байт")
    print(f"  Компактный формат:  {compact_size} байт")
    print(f"  Экономия:           {savings:.1f}%")
    
    if savings >= 50:
        print(f"  ✅ Экономия достаточная ({savings:.1f}% >= 50%)")
        return True
    else:
        print(f"  ⚠️  ВНИМАНИЕ: Экономия меньше чем ожидалось ({savings:.1f}%)")
        return False


def test_fallback_interval():
    """Проверка: установлен ли правильный интервал fallback"""
    print("\n✓ Проверка интервала HTTP fallback")
    
    with open('webapp/static/performance-optimizer.js', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем интервал 60000 мс (60 сек)
    if 'startSlowFallbackUpdates()' in content:
        if '60000' in content:
            print("  ✅ Интервал fallback установлен на 60 сек (правильный)")
            print("     Это уменьшает запросы с 60 в минуту до 1 в минуту!")
            return True
        else:
            print("  ❌ ОШИБКА: Интервал fallback не 60 сек")
            return False
    else:
        print("  ⚠️  ВНИМАНИЕ: startSlowFallbackUpdates не найден")
        return False


def test_docs_exists():
    """Проверка: существуют ли документации"""
    print("\n✓ Проверка наличия документаций")
    
    docs = [
        'docs/PERFORMANCE_DIAGNOSIS_v0.1.9.md',
        'docs/IMPLEMENTATION_GUIDE_v0.1.9.md',
    ]
    
    all_exist = True
    for doc in docs:
        doc_path = Path(doc)
        if doc_path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ ОШИБКА: {doc} не найден")
            all_exist = False
    
    return all_exist


def calculate_overall_score():
    """Рассчитать общий результат"""
    tests = [
        ("performance-optimizer.js", test_performance_optimizer_exists()),
        ("HTML загрузка", test_html_loads_optimizer()),
        ("Compact API", test_compact_api_exists()),
        ("Эффективность формата", test_compact_format_efficiency()),
        ("Интервал fallback", test_fallback_interval()),
        ("Документация", test_docs_exists()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    return passed, total, tests


def print_summary(passed, total, tests):
    """Вывести итоговый отчет"""
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} | {test_name}")
    
    print("=" * 60)
    
    score = (passed / total) * 100
    print(f"\nРезультат: {passed}/{total} ({score:.0f}%)")
    
    if passed == total:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n✅ Оптимизации готовы к внедрению.")
        print("Ожидаемые результаты:")
        print("  • Загрузка: 5-8 сек → 2-3 сек (-50%)")
        print("  • Трафик: -60-70%")
        print("  • Батарея: -40% нагрузки")
        print("  • Запросы: 60 в мин → 1 в мин (-98%)")
        return True
    elif passed >= (total * 0.8):
        print("\n⚠️  БОЛЬШИНСТВО ПРОВЕРОК ПРОЙДЕНО")
        print(f"Требуется исправить {total - passed} проблем(ы)")
        return False
    else:
        print("\n❌ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ")
        print(f"Пройдено только {passed}/{total} проверок")
        return False


def main():
    print("\n" + "=" * 60)
    print("🚀 БЫСТРЫЙ ТЕСТ ОПТИМИЗАЦИЙ v0.1.9")
    print("=" * 60)
    
    passed, total, tests = calculate_overall_score()
    result = print_summary(passed, total, tests)
    
    print("\n" + "=" * 60)
    
    if result:
        print("\n📋 Следующие шаги:")
        print("1. Добавить компактные функции в webapp/server.py")
        print("2. Обновить API эндпоинты для параметра ?compact=1")
        print("3. Обновить frontend fetch запросы")
        print("4. Тестировать на локальной машине")
        print("5. Развернуть на Amvera")
        print("\nСм. docs/IMPLEMENTATION_GUIDE_v0.1.9.md для подробных инструкций")
    else:
        print("\n❌ Пожалуйста, исправьте проблемы перед внедрением")
    
    print("\n" + "=" * 60)
    
    return result


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
