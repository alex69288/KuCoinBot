"""
Очистка position_state.json от дублирующих старых полей
"""
import json

# Загружаем
with open('position_state.json', 'r') as f:
    state = json.load(f)

# Очищаем каждую пару
for pair_symbol, pair_data in state.items():
    # Удаляем старые поля из корня
    old_fields = ['position', 'entry_price', 'position_size_usdt', 'opened_at', 
                  'strategy_position_size_usdt', 'strategy_entry_price']
    
    for field in old_fields:
        if field in pair_data:
            print(f"🧹 Удаляем старое поле '{field}' из {pair_symbol}")
            del pair_data[field]
    
    # Проверяем, что есть новые поля
    if 'positions' not in pair_data:
        pair_data['positions'] = []
        pair_data['total_position_size_usdt'] = 0
        pair_data['average_entry_price'] = 0
        pair_data['max_entry_price'] = 0
        pair_data['total_amount_crypto'] = 0
        pair_data['next_position_id'] = 1

# Сохраняем чистую версию
with open('position_state.json', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("\n✅ Файл очищен!")
print("\n📊 Текущее состояние:")
print(json.dumps(state, indent=2, ensure_ascii=False))
