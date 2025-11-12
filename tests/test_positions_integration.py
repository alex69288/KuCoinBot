"""
Интеграционный тест для проверки корректной работы подсчета открытых позиций
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_position_state_file():
    """Проверяем структуру position_state.json"""
    print("\n📋 [ТЕСТ 1] Структура position_state.json")
    print("=" * 60)
    
    if not os.path.exists('position_state.json'):
        print("❌ Ошибка: position_state.json не найден!")
        return False
    
    try:
        with open('position_state.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ Файл успешно прочитан с кодировкой UTF-8")
    except UnicodeDecodeError:
        print("❌ Ошибка кодировки файла!")
        return False
    
    # Проверяем структуру
    total_positions = 0
    for pair, pair_data in data.items():
        print(f"\n  📍 {pair}")
        
        if not isinstance(pair_data, dict):
            print(f"  ❌ Данные пары не являются словарём!")
            return False
        
        if 'positions' not in pair_data:
            print(f"  ❌ Отсутствует поле 'positions'!")
            return False
        
        positions_count = len(pair_data['positions'])
        total_positions += positions_count
        
        print(f"    - Открытых позиций: {positions_count}")
        print(f"    - Общий размер: {pair_data.get('total_position_size_usdt', 0)} USDT")
        print(f"    - Средняя цена входа: {pair_data.get('average_entry_price', 0):.2f}")
        
        # Проверяем каждую позицию
        for pos in pair_data['positions']:
            required_fields = ['id', 'entry_price', 'position_size_usdt', 'amount_crypto']
            missing_fields = [f for f in required_fields if f not in pos]
            
            if missing_fields:
                print(f"    ❌ Позиция {pos.get('id')}: отсутствуют поля {missing_fields}")
                return False
            
            print(f"      ✓ ID {pos['id']}: {pos['position_size_usdt']} USDT @ {pos['entry_price']:.2f}")
    
    print(f"\n✅ Итого открытых позиций: {total_positions}")
    return total_positions > 0


def test_position_manager():
    """Проверяем функции position_manager.py"""
    print("\n📋 [ТЕСТ 2] Функции position_manager.py")
    print("=" * 60)
    
    try:
        from utils.position_manager import load_position_state, get_positions_count
        print("✅ Модуль position_manager успешно импортирован")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Тест load_position_state
    try:
        state = load_position_state('position_state.json')
        print("✅ Функция load_position_state() работает")
    except Exception as e:
        print(f"❌ Ошибка в load_position_state(): {e}")
        return False
    
    # Тест get_positions_count
    try:
        for pair in state.keys():
            count = get_positions_count(pair)
            expected_count = len(state[pair].get('positions', []))
            if count == expected_count:
                print(f"✅ {pair}: {count} позиций (верно)")
            else:
                print(f"❌ {pair}: функция вернула {count}, ожидалось {expected_count}")
                return False
    except Exception as e:
        print(f"❌ Ошибка в get_positions_count(): {e}")
        return False
    
    return True


def test_api_endpoints_simulation():
    """Имитируем работу API endpoints"""
    print("\n📋 [ТЕСТ 3] Имитация API endpoints")
    print("=" * 60)
    
    from utils.position_manager import load_position_state
    
    # Endpoint /api/positions
    print("\n  🔌 Endpoint /api/positions")
    state = load_position_state('position_state.json')
    positions = []
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            for pos_data in pair_data.get('positions', []):
                positions.append({
                    "id": f"{pair_symbol}_{pos_data.get('id', 0)}",
                    "pair": pair_symbol,
                    "status": "long",
                    "entry_price": pos_data.get('entry_price', 0),
                    "current_price": pos_data.get('entry_price', 0) * 1.01,
                    "amount": pos_data.get('amount_crypto', 0),
                    "position_size_usdt": pos_data.get('position_size_usdt', 0),
                })
    
    print(f"    ✅ Возвращает {len(positions)} позиций")
    
    # Endpoint /api/status
    print("\n  🔌 Endpoint /api/status")
    total_open_positions = 0
    total_position_size_usdt = 0
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            total_open_positions += len(positions_list)
            total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
    
    print(f"    ✅ open_count: {total_open_positions}")
    print(f"    ✅ size_usdt: {total_position_size_usdt}")
    
    # Проверяем соответствие
    if total_open_positions == len(positions):
        print(f"\n✅ Количество позиций соответствует: {total_open_positions}")
        return True
    else:
        print(f"\n❌ Несоответствие: /api/positions вернул {len(positions)}, "
              f"/api/status указывает {total_open_positions}")
        return False


def test_frontend_compatibility():
    """Проверяем совместимость с frontend кодом"""
    print("\n📋 [ТЕСТ 4] Совместимость с frontend")
    print("=" * 60)
    
    # Проверяем что HTML файл обновлён
    if not os.path.exists('webapp/static/index.html'):
        print("❌ Файл webapp/static/index.html не найден!")
        return False
    
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Проверяем нужные изменения
    checks = [
        ('loadPositions', 'Функция loadPositions присутствует'),
        ('pos.pair', 'Используется поле pair вместо symbol'),
        ('pos.position_size_usdt', 'Отображается position_size_usdt'),
        ('pos.pnl_percent', 'Отображается процент PnL'),
        ('/api/positions', 'Используется endpoint /api/positions'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in html_content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
            all_passed = False
    
    return all_passed


def main():
    print("\n" + "=" * 60)
    print("🧪 ИНТЕГРАЦИОННЫЙ ТЕСТ: Подсчет открытых позиций")
    print("=" * 60)
    
    tests = [
        ("Структура position_state.json", test_position_state_file),
        ("Функции position_manager", test_position_manager),
        ("Имитация API endpoints", test_api_endpoints_simulation),
        ("Совместимость с frontend", test_frontend_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ИСКЛЮЧЕНИЕ в тесте '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Финальный отчет
    print("\n" + "=" * 60)
    print("📊 ФИНАЛЬНЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    print(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ {total - passed} тест(ов) провалено")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
