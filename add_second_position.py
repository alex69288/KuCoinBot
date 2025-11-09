"""
Добавление второй позиции вручную
"""
import json
from datetime import datetime

# Читаем текущий state
with open('position_state.json', 'r') as f:
    state = json.load(f)

btc_pair = state.get('BTC/USDT', {})

# Данные первой покупки (которой не было в state)
position_1 = {
    'id': 1,
    'entry_price': 110185.7,
    'position_size_usdt': 1.1,
    'amount_crypto': 1.1 / 110185.7,  # Рассчитываем количество BTC
    'opened_at': int(datetime(2025, 11, 2, 0, 40).timestamp() * 1000),
    'order_id': None,
    'is_legacy': False,
    'note': 'Первая покупка (добавлена вручную)'
}

# Данные второй покупки (из API)
position_2 = {
    'id': 2,
    'entry_price': 103573.5,
    'position_size_usdt': 1.0,
    'amount_crypto': 1.0 / 103573.5,
    'opened_at': int(datetime(2025, 11, 5, 19, 41).timestamp() * 1000),
    'order_id': None,
    'is_legacy': False,
    'note': 'Вторая покупка'
}

# Обновляем структуру
btc_pair['positions'] = [position_1, position_2]

# Пересчитываем итоги
total_amount = position_1['amount_crypto'] + position_2['amount_crypto']
total_cost = position_1['position_size_usdt'] + position_2['position_size_usdt']

btc_pair['total_position_size_usdt'] = total_cost
btc_pair['total_amount_crypto'] = total_amount
btc_pair['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
btc_pair['next_position_id'] = 3

# ⚠️ ВАЖНАЯ ЛОГИКА: для Take Profit используем МАКСИМАЛЬНУЮ цену входа
btc_pair['max_entry_price'] = max(position_1['entry_price'], position_2['entry_price'])

state['BTC/USDT'] = btc_pair

# Сохраняем
with open('position_state.json', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("=" * 70)
print("✅ ПОЗИЦИИ ОБНОВЛЕНЫ")
print("=" * 70)

print(f"\n📊 Позиция 1:")
print(f"   Цена входа: {position_1['entry_price']:,.2f} USDT")
print(f"   Размер: {position_1['position_size_usdt']:.2f} USDT")
print(f"   Количество: {position_1['amount_crypto']:.8f} BTC")

print(f"\n📊 Позиция 2:")
print(f"   Цена входа: {position_2['entry_price']:,.2f} USDT")
print(f"   Размер: {position_2['position_size_usdt']:.2f} USDT")
print(f"   Количество: {position_2['amount_crypto']:.8f} BTC")

print(f"\n💰 ИТОГО:")
print(f"   Количество позиций: 2")
print(f"   Общая ставка: {total_cost:.2f} USDT")
print(f"   Общее количество: {total_amount:.8f} BTC")
print(f"   Средняя цена: {btc_pair['average_entry_price']:,.2f} USDT")
print(f"   ⚠️ Цена для TP (max): {btc_pair['max_entry_price']:,.2f} USDT")

print("\n" + "=" * 70)
