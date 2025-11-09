"""
Попытка восстановить недостающую позицию через баланс
"""
import json
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем текущий баланс
ex = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_SECRET_KEY'),
    'password': os.getenv('KUCOIN_PASSPHRASE')
})

balance = ex.fetch_balance()
btc_total = balance['BTC']['total']

print("=" * 60)
print("АНАЛИЗ РАСХОЖДЕНИЯ БАЛАНСА И POSITION_STATE")
print("=" * 60)

# Читаем position_state
with open('position_state.json', 'r') as f:
    state = json.load(f)

btc_state = state.get('BTC/USDT', {})
positions = btc_state.get('positions', [])
total_amount_in_state = btc_state.get('total_amount_crypto', 0)

print(f"\n📊 Баланс на бирже: {btc_total:.8f} BTC")
print(f"📊 В position_state: {total_amount_in_state:.8f} BTC")
print(f"📊 Позиций в state: {len(positions)}")

difference = btc_total - total_amount_in_state

if abs(difference) > 0.000001:  # Если разница > 1 satoshi
    print(f"\n⚠️  РАСХОЖДЕНИЕ: {difference:.8f} BTC")
    print(f"\n💡 Возможные причины:")
    print(f"   1. Была еще одна покупка, которую бот не отследил")
    print(f"   2. Перевод BTC извне")
    print(f"   3. Старая покупка до начала работы бота")
    
    # Пробуем восстановить
    if difference > 0:
        print(f"\n🔧 ПОПЫТКА ВОССТАНОВЛЕНИЯ:")
        print(f"   Недостающее количество: {difference:.8f} BTC")
        
        # Получаем текущую цену для оценки
        ticker = ex.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        estimated_usdt = difference * current_price
        
        print(f"   Текущая цена BTC: {current_price:,.2f} USDT")
        print(f"   Оценочная стоимость: {estimated_usdt:.2f} USDT")
        
        print(f"\n❓ ВАРИАНТЫ ДЕЙСТВИЙ:")
        print(f"   A) Игнорировать - считать legacy позицию как агрегированную")
        print(f"   B) Создать вторую 'unknown' позицию с оценочной ценой")
        print(f"   C) Вручную указать детали второй покупки")
        
        choice = input("\nВыберите вариант (A/B/C): ").upper()
        
        if choice == 'B':
            # Создаем unknown позицию
            unknown_position = {
                'id': 'unknown_1',
                'entry_price': current_price,  # Используем текущую как приближение
                'position_size_usdt': estimated_usdt,
                'amount_crypto': difference,
                'opened_at': 0,  # Неизвестно
                'order_id': None,
                'is_legacy': True,
                'note': 'Восстановленная позиция (детали неизвестны)'
            }
            
            # Добавляем в positions
            positions.append(unknown_position)
            
            # Пересчитываем total
            btc_state['positions'] = positions
            btc_state['total_amount_crypto'] = btc_total
            btc_state['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in positions)
            
            # Пересчитываем среднюю цену
            total_cost = sum(p['position_size_usdt'] for p in positions)
            btc_state['average_entry_price'] = total_cost / btc_total if btc_total > 0 else 0
            
            # Сохраняем
            state['BTC/USDT'] = btc_state
            with open('position_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"\n✅ Добавлена 'unknown' позиция")
            print(f"✅ Теперь позиций: {len(positions)}")
            print(f"✅ Общий баланс: {btc_total:.8f} BTC")
            
        elif choice == 'C':
            print("\nВведите детали второй покупки:")
            entry_price = float(input("  Цена входа (USDT): "))
            amount_btc = float(input("  Количество (BTC): "))
            
            manual_position = {
                'id': 'manual_1',
                'entry_price': entry_price,
                'position_size_usdt': entry_price * amount_btc,
                'amount_crypto': amount_btc,
                'opened_at': 0,
                'order_id': None,
                'is_legacy': True,
                'note': 'Вручную добавленная позиция'
            }
            
            positions.append(manual_position)
            btc_state['positions'] = positions
            btc_state['total_amount_crypto'] = sum(p['amount_crypto'] for p in positions)
            btc_state['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in positions)
            total_amount = sum(p['amount_crypto'] for p in positions)
            total_cost = sum(p['position_size_usdt'] for p in positions)
            btc_state['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
            
            state['BTC/USDT'] = btc_state
            with open('position_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"\n✅ Добавлена вручную позиция")
            print(f"✅ Теперь позиций: {len(positions)}")
        else:
            print("\n✅ Оставляем как есть - legacy позиция считается агрегированной")
else:
    print(f"\n✅ Баланс совпадает с position_state")
