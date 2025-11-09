"""
Миграция position_state.json к новой структуре с массивом позиций
"""
import json
import os
from datetime import datetime

def migrate_position_state():
    """Мигрирует старую структуру position_state.json к новой"""
    
    state_file = 'position_state.json'
    backup_file = f'position_state_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    if not os.path.exists(state_file):
        print(f"❌ Файл {state_file} не найден!")
        return False
    
    # Создаем бэкап
    with open(state_file, 'r') as f:
        old_data = json.load(f)
    
    with open(backup_file, 'w') as f:
        json.dump(old_data, f, indent=2)
    print(f"✅ Создан бэкап: {backup_file}")
    
    # Мигрируем данные
    new_data = {}
    
    for pair_symbol, pair_data in old_data.items():
        position_size = pair_data.get('position_size_usdt', 0)
        entry_price = pair_data.get('entry_price', 0)
        
        if position_size > 0 and entry_price > 0:
            # Есть открытая позиция - создаем массив с одной "legacy" позицией
            # Это агрегированная позиция, т.к. мы не знаем детали отдельных покупок
            amount_crypto = position_size / entry_price if entry_price > 0 else 0
            new_data[pair_symbol] = {
                'positions': [
                    {
                        'id': 'legacy_1',  # Помечаем как legacy
                        'entry_price': entry_price,
                        'position_size_usdt': position_size,
                        'amount_crypto': amount_crypto,
                        'opened_at': pair_data.get('opened_at', 0),
                        'order_id': None,
                        'is_legacy': True,  # Флаг для особой обработки
                        'note': 'Агрегированная позиция из старой системы'
                    }
                ],
                'total_position_size_usdt': position_size,
                'average_entry_price': entry_price,
                'total_amount_crypto': amount_crypto,
                'next_position_id': 2  # Следующий ID для новых позиций
            }
            print(f"✅ Мигрирована пара {pair_symbol}: 1 legacy позиция на {position_size:.2f} USDT @ {entry_price:.2f}")
        else:
            # Нет открытой позиции
            new_data[pair_symbol] = {
                'positions': [],
                'total_position_size_usdt': 0,
                'average_entry_price': 0,
                'total_amount_crypto': 0,
                'next_position_id': 1
            }
            print(f"✅ Мигрирована пара {pair_symbol}: позиций нет")
    
    # Сохраняем новую структуру
    with open(state_file, 'w') as f:
        json.dump(new_data, f, indent=2)
    
    print(f"\n✅ Миграция завершена! Старая версия сохранена в {backup_file}")
    print("\n📊 Новая структура:")
    print(json.dumps(new_data, indent=2))
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("МИГРАЦИЯ position_state.json")
    print("=" * 60)
    print("\nЭтот скрипт изменит структуру position_state.json")
    print("Старая версия будет сохранена в бэкап.\n")
    
    response = input("Продолжить? (yes/no): ")
    if response.lower() in ['yes', 'y', 'да', 'д']:
        migrate_position_state()
    else:
        print("❌ Миграция отменена")
