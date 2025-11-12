"""
Тест для диагностики проблемы загрузки позиций
"""
import sys
import os
import json

# Добавляем корневую папку в пути поиска
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.position_manager import load_position_state

def test_position_state_loading():
    """Проверяет загрузку position_state.json"""
    print("\n" + "="*70)
    print("🔍 ТЕСТ ЗАГРУЗКИ POSITION_STATE")
    print("="*70)
    
    # Проверяем существование файла
    file_path = 'position_state.json'
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не найден!")
        return False
    
    print(f"✅ Файл {file_path} найден")
    print(f"   Размер: {os.path.getsize(file_path)} байт")
    
    # Загружаем файл напрямую
    print("\n📖 Содержимое position_state.json:")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = json.load(f)
        print("✅ JSON успешно прочитан")
    except Exception as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return False
    
    # Используем функцию load_position_state
    print("\n🔄 Загрузка через load_position_state():")
    try:
        state = load_position_state(file_path)
        print("✅ load_position_state() успешно выполнена")
    except Exception as e:
        print(f"❌ Ошибка load_position_state(): {e}")
        return False
    
    # Анализируем содержимое
    print("\n📊 Анализ позиций:")
    if not state:
        print("⚠️  state пуста!")
        return False
    
    total_positions = 0
    total_usdt = 0
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict):
            positions_list = pair_data.get('positions', [])
            total_usdt += pair_data.get('total_position_size_usdt', 0)
            total_positions += len(positions_list)
            
            print(f"\n   📌 {pair_symbol}:")
            print(f"      - Открытых позиций: {len(positions_list)}")
            print(f"      - Общий размер USDT: {pair_data.get('total_position_size_usdt', 0)}")
            print(f"      - Средняя цена входа: {pair_data.get('average_entry_price', 0)}")
            
            if positions_list:
                for idx, pos in enumerate(positions_list, 1):
                    print(f"        Позиция {idx}:")
                    print(f"          - ID: {pos.get('id')}")
                    print(f"          - Цена входа: {pos.get('entry_price')}")
                    print(f"          - Размер USDT: {pos.get('position_size_usdt')}")
                    print(f"          - Объем крипто: {pos.get('amount_crypto')}")
    
    print(f"\n📈 ИТОГО:")
    print(f"   - Всего открытых позиций: {total_positions}")
    print(f"   - Всего USDT в позициях: {total_usdt}")
    
    if total_positions > 0:
        print("✅ Позиции успешно загружены!")
        return True
    else:
        print("⚠️  Позиции не найдены в файле")
        return False

def test_api_response_format():
    """Проверяет формат API ответа"""
    print("\n" + "="*70)
    print("🔍 ТЕСТ ФОРМАТА API ОТВЕТА")
    print("="*70)
    
    state = load_position_state('position_state.json')
    
    # Симулируем формат API
    total_open_positions = 0
    total_position_size_usdt = 0
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            total_open_positions += len(positions_list)
            total_position_size_usdt += pair_data.get('total_position_size_usdt', 0)
    
    # Формируем ответ как в API
    positions_info = {
        "open_count": total_open_positions,
        "size_usdt": total_position_size_usdt,
        "entry_price": 0,
        "current_profit_percent": 0,
        "current_profit_usdt": 0,
        "to_take_profit": 0,
        "tp_target": 2.0,
        "fee_percent": 0.2,
        "fee_usdt": 0
    }
    
    full_response = {
        "positions": positions_info,
        "last_update": "2025-11-12T00:00:00"
    }
    
    print("\n📤 Формат API ответа:")
    print(json.dumps(full_response, indent=2, ensure_ascii=False))
    
    if positions_info["open_count"] > 0:
        print("\n✅ API ответ содержит позиции!")
        return True
    else:
        print("\n⚠️  API ответ не содержит позиций!")
        return False

if __name__ == '__main__':
    try:
        # Запускаем тесты
        test1_ok = test_position_state_loading()
        test2_ok = test_api_response_format()
        
        print("\n" + "="*70)
        print("📋 РЕЗЮМЕ ТЕСТИРОВАНИЯ")
        print("="*70)
        
        if test1_ok and test2_ok:
            print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
            print("\n💡 ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМЫ:")
            print("   1. Позиции не отправляются клиенту (проблема на фронтенде)")
            print("   2. Проблема с аутентификацией Telegram (401 ошибка)")
            print("   3. Проблема с кэшированием в браузере")
            sys.exit(0)
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
