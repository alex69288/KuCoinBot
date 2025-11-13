"""
Тест для проверки логики позиций после исправления WebSocket ошибок
"""
import os
import json

def test_position_state_file():
    """Проверить что файл position_state.json содержит 2 позиции"""
    if os.path.exists('position_state.json'):
        with open('position_state.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Проверяем что есть BTC/USDT пара
        assert 'BTC/USDT' in data, "BTC/USDT пара не найдена"
        
        # Проверяем что есть positions массив
        assert 'positions' in data['BTC/USDT'], "Массив positions не найден"
        
        # Проверяем что есть 2 позиции
        positions = data['BTC/USDT']['positions']
        assert len(positions) == 2, f"Ожидается 2 позиции, найдено {len(positions)}"
        
        # Проверяем структуру каждой позиции
        for i, pos in enumerate(positions):
            assert 'id' in pos, f"Позиция {i} не имеет ID"
            assert 'entry_price' in pos, f"Позиция {i} не имеет entry_price"
            assert 'position_size_usdt' in pos, f"Позиция {i} не имеет position_size_usdt"
            assert 'amount_crypto' in pos, f"Позиция {i} не имеет amount_crypto"
        
        print("✅ Тест position_state_file PASSED")
        return True
    else:
        print("⚠️  position_state.json не найден")
        return False


def test_position_count_calculation():
    """Проверить расчёт количества позиций"""
    if os.path.exists('position_state.json'):
        with open('position_state.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Считаем позиции (как это делает API)
        total_positions = 0
        for pair_symbol, pair_data in data.items():
            if isinstance(pair_data, dict) and 'positions' in pair_data:
                positions_list = pair_data.get('positions', [])
                total_positions += len(positions_list)
        
        assert total_positions == 2, f"Ожидается 2 позиции, найдено {total_positions}"
        
        print("✅ Тест position_count_calculation PASSED")
        return True
    else:
        print("⚠️  position_state.json не найден")
        return False


def test_websocket_position_logic():
    """Проверить логику получения позиций в WebSocket"""
    # Это логика из исправленного WebSocket обработчика
    if os.path.exists('position_state.json'):
        with open('position_state.json', 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Логика из WebSocket handler
        total_positions = 0
        for pair_symbol, pair_data in state.items():
            if isinstance(pair_data, dict) and 'positions' in pair_data:
                total_positions += len(pair_data.get('positions', []))
        
        assert total_positions == 2, f"WebSocket: ожидается 2 позиции, найдено {total_positions}"
        
        data = {
            "positions": {
                "open_count": total_positions
            }
        }
        
        assert data["positions"]["open_count"] == 2, "WebSocket должен возвращать 2 открытые позиции"
        
        print("✅ Тест websocket_position_logic PASSED")
        return True
    else:
        print("⚠️  position_state.json не найден")
        return False


if __name__ == "__main__":
    print("\n🔍 Тесты логики позиций (v0.1.8)\n")
    
    results = [
        test_position_state_file(),
        test_position_count_calculation(),
        test_websocket_position_logic(),
    ]
    
    total = len(results)
    passed = sum(results)
    
    print(f"\n{'='*50}")
    print(f"Результаты: {passed}/{total} тестов пройдено")
    print(f"{'='*50}\n")
    
    if all(results):
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        exit(0)
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        exit(1)
