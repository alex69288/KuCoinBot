"""
Тест проверки правильного отображения количества открытых позиций
"""
import json
import os
import sys

# Добавляем путь к корневой папке проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_position_state_structure():
    """Тест: Проверяем структуру position_state.json"""
    position_file = 'position_state.json'
    
    if not os.path.exists(position_file):
        print("⚠️ position_state.json не найден")
        return False
    
    with open(position_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📄 Структура position_state.json:")
    
    total_positions = 0
    for pair, pair_data in data.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_count = len(pair_data['positions'])
            total_positions += positions_count
            print(f"  {pair}: {positions_count} позиций")
            print(f"    - total_position_size_usdt: {pair_data.get('total_position_size_usdt', 0)}")
            print(f"    - average_entry_price: {pair_data.get('average_entry_price', 0)}")
            
            # Выводим каждую позицию
            for pos in pair_data['positions']:
                print(f"      - ID {pos.get('id')}: {pos.get('position_size_usdt')} USDT @ {pos.get('entry_price')}")
    
    print(f"\n✅ ВСЕГО ОТКРЫТЫХ ПОЗИЦИЙ: {total_positions}")
    return total_positions


def test_api_endpoint_simulation():
    """Тест: Имитируем работу API endpoint /api/positions"""
    from utils.position_manager import load_position_state
    
    state = load_position_state('position_state.json')
    positions = []
    
    # Имитируем код из get_positions endpoint
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            for pos_data in pair_data.get('positions', []):
                # Имитируем получение текущей цены
                current_price = pos_data.get('entry_price', 0) * 1.01  # Просто для примера
                entry_price = pos_data.get('entry_price', 0)
                position_size_usdt = pos_data.get('position_size_usdt', 0)
                
                pnl = 0
                if entry_price > 0 and current_price > 0:
                    pnl = (current_price - entry_price) * position_size_usdt / entry_price
                
                positions.append({
                    "id": f"{pair_symbol}_{pos_data.get('id', 0)}",
                    "pair": pair_symbol,
                    "status": "long",
                    "entry_price": entry_price,
                    "current_price": current_price,
                    "amount": pos_data.get('amount_crypto', 0),
                    "position_size_usdt": position_size_usdt,
                    "pnl": pnl,
                    "pnl_percent": ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0,
                    "opened_at": pos_data.get('opened_at', 0)
                })
    
    print(f"\n📊 Ответ от /api/positions:")
    print(f"Количество позиций в ответе: {len(positions)}")
    
    for pos in positions:
        print(f"  {pos['pair']} (ID: {pos['id']})")
        print(f"    - Размер: {pos['position_size_usdt']} USDT")
        print(f"    - Цена входа: {pos['entry_price']}")
        print(f"    - Текущая цена: {pos['current_price']:.2f}")
        print(f"    - PnL: {pos['pnl']:.4f} USDT ({pos['pnl_percent']:.2f}%)")
    
    return len(positions)


def test_status_endpoint_simulation():
    """Тест: Имитируем работу API endpoint /api/status"""
    from utils.position_manager import load_position_state
    
    total_open_positions = 0
    total_position_size_usdt = 0
    
    state = load_position_state('position_state.json')
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            total_open_positions += len(positions_list)
            total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
    
    print(f"\n📊 Ответ от /api/status (поле positions):")
    print(f"  open_count: {total_open_positions}")
    print(f"  size_usdt: {total_position_size_usdt}")
    
    return total_open_positions


def main():
    print("=" * 60)
    print("🔍 ТЕСТ: Проверка количества открытых позиций")
    print("=" * 60)
    
    # Тест 1: Проверяем структуру position_state.json
    print("\n[ТЕСТ 1] Структура position_state.json")
    total_positions = test_position_state_structure()
    
    # Тест 2: Проверяем endpoint /api/positions
    print("\n[ТЕСТ 2] Endpoint /api/positions")
    api_positions_count = test_api_endpoint_simulation()
    
    # Тест 3: Проверяем endpoint /api/status
    print("\n[ТЕСТ 3] Endpoint /api/status")
    status_positions_count = test_status_endpoint_simulation()
    
    # Проверяем соответствие
    print("\n" + "=" * 60)
    print("✅ РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print("=" * 60)
    
    if total_positions == api_positions_count == status_positions_count:
        print(f"✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print(f"✅ Количество открытых позиций: {total_positions}")
        return True
    else:
        print(f"❌ ОШИБКА: Количество позиций не совпадает!")
        print(f"  - position_state.json: {total_positions}")
        print(f"  - /api/positions: {api_positions_count}")
        print(f"  - /api/status: {status_positions_count}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
