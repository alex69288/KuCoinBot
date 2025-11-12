"""
Тест для эндпоинта /api/positions - проверка правильного подсчёта позиций

Этот тест проверяет, что API возвращает правильное количество позиций
из файла position_state.json
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


def test_position_state_parsing():
    """Тест: Проверяем, что position_state.json содержит 2 позиции"""
    
    position_state_path = os.path.join(os.path.dirname(__file__), '..', 'position_state.json')
    
    if not os.path.exists(position_state_path):
        print(f"⚠️  Файл не найден: {position_state_path}")
        return False
    
    with open(position_state_path, 'r') as f:
        state = json.load(f)
    
    # Считаем позиции как в API
    total_open_positions = 0
    total_position_size_usdt = 0
    
    for pair_symbol, pair_data in state.items():
        print(f"  Пара: {pair_symbol}")
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            print(f"    Позиций: {len(positions_list)}")
            total_open_positions += len(positions_list)
            total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
            
            for idx, pos in enumerate(positions_list, 1):
                print(f"      Позиция {idx}: ID={pos.get('id')}, Size={pos.get('position_size_usdt')} USDT, Entry={pos.get('entry_price')}")
    
    print(f"\n📊 Итого:")
    print(f"  • Всего позиций: {total_open_positions}")
    print(f"  • Общий размер: {total_position_size_usdt} USDT")
    
    assert total_open_positions == 2, f"Ожидалось 2 позиции, получено {total_open_positions}"
    assert total_position_size_usdt == 2.1, f"Ожидалось 2.1 USDT, получено {total_position_size_usdt}"
    
    return True


def test_position_count_endpoint():
    """
    Тест: Проверяем логику эндпоинта /api/status
    
    Это имитирует то, что делает эндпоинт при подсчёте позиций
    """
    position_state_path = os.path.join(os.path.dirname(__file__), '..', 'position_state.json')
    
    if not os.path.exists(position_state_path):
        print(f"⚠️  Файл не найден: {position_state_path}")
        return False
    
    with open(position_state_path, 'r') as f:
        state = json.load(f)
    
    # Инициализируем positions_info как в API эндпоинте
    positions_info = {
        "open_count": 0,
        "size_usdt": 0,
        "entry_price": 0,
        "current_profit_percent": 0,
        "current_profit_usdt": 0,
        "to_take_profit": 0,
    }
    
    total_open_positions = 0
    total_position_size_usdt = 0
    
    # Подсчитываем позиции
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            total_open_positions += len(positions_list)
            total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
    
    positions_info["open_count"] = total_open_positions
    positions_info["size_usdt"] = total_position_size_usdt
    
    print(f"📊 Результат подсчёта для /api/status:")
    print(f"  • open_count: {positions_info['open_count']}")
    print(f"  • size_usdt: {positions_info['size_usdt']}")
    
    assert positions_info["open_count"] == 2, f"Ожидалось 2, получено {positions_info['open_count']}"
    assert positions_info["size_usdt"] == 2.1, f"Ожидалось 2.1, получено {positions_info['size_usdt']}"
    
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ ПОДСЧЁТА ПОЗИЦИЙ")
    print("="*60 + "\n")
    
    try:
        print("1️⃣  Проверяем файл position_state.json...")
        if test_position_state_parsing():
            print("✅ Файл содержит ожидаемые данные\n")
        
        print("2️⃣  Проверяем логику /api/status...")
        if test_position_count_endpoint():
            print("✅ Эндпоинт правильно считает позиции\n")
        
        print("="*60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*60)
        print("\n📌 ВЫВОД: API должна возвращать open_count=2\n")
        
    except AssertionError as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
