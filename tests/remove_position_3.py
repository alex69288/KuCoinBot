"""
Удаление позиции #3 (последняя)
"""
import json

with open('position_state.json', 'r') as f:
    state = json.load(f)

btc = state['BTC/USDT']

print("📊 ТЕКУЩИЕ ПОЗИЦИИ:")
for pos in btc['positions']:
    print(f"  #{pos['id']}: {pos['entry_price']:,.2f} USDT - {pos['position_size_usdt']:.2f} USDT")

print("\nУдаляю позицию #3...")

# Удаляем последнюю позицию
if len(btc['positions']) >= 3:
    removed = btc['positions'].pop()  # Удаляем последнюю
    print(f"❌ Удалена позиция #{removed['id']}: {removed['entry_price']:,.2f} USDT")
    
    # Пересчитываем итоги
    btc['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in btc['positions'])
    btc['total_amount_crypto'] = sum(p['amount_crypto'] for p in btc['positions'])
    
    if btc['positions']:
        total_cost = btc['total_position_size_usdt']
        total_amount = btc['total_amount_crypto']
        btc['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
        btc['max_entry_price'] = max(p['entry_price'] for p in btc['positions'])
    
    # Сохраняем
    with open('position_state.json', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print("\n✅ ОСТАЛОСЬ ПОЗИЦИЙ: 2")
    print(f"💰 Общая ставка: {btc['total_position_size_usdt']:.2f} USDT")
    print(f"📈 Max цена для TP: {btc['max_entry_price']:,.2f} USDT")
else:
    print("⚠️ Недостаточно позиций для удаления")
