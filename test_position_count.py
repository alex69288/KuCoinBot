"""
Тестовый скрипт для проверки подсчета открытых позиций
"""
import json
import os

# Читаем position_state.json
state_file = 'position_state.json'
if os.path.exists(state_file):
    with open(state_file, 'r') as f:
        position_state = json.load(f)
    
    print("=" * 50)
    print("АНАЛИЗ ОТКРЫТЫХ ПОЗИЦИЙ")
    print("=" * 50)
    
    for pair, data in position_state.items():
        position_size = data.get('position_size_usdt', 0)
        entry_price = data.get('entry_price', 0)
        position_status = data.get('position', None)
        
        print(f"\n📊 Пара: {pair}")
        print(f"   Статус: {position_status}")
        print(f"   Размер позиции: {position_size} USDT")
        print(f"   Цена входа: {entry_price}")
        print(f"   Открыта: {'✅ ДА' if position_size > 0 else '❌ НЕТ'}")
    
    # Подсчет открытых позиций
    open_positions_count = sum(1 for pair_data in position_state.values() 
                              if pair_data.get('position_size_usdt', 0) > 0)
    
    print("\n" + "=" * 50)
    print(f"📈 ИТОГО ОТКРЫТЫХ ПОЗИЦИЙ: {open_positions_count}")
    print("=" * 50)
else:
    print(f"❌ Файл {state_file} не найден!")
