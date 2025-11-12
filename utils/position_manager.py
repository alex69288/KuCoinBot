"""
Вспомогательные функции для работы с position_state.json (новая структура с массивом)
"""
import json
import os
from datetime import datetime

def load_position_state(file_path='position_state.json'):
    """Загружает position_state, конвертирует старый формат в новый если нужно"""
    if not os.path.exists(file_path):
        return {}
    
    # Пробуем разные кодировки
    for encoding in ['latin-1', 'utf-8', 'utf-16']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    else:
        # Если ничего не сработало, используем стандартную
        with open(file_path, 'r') as f:
            data = json.load(f)
    
    # Проверяем и конвертируем старый формат
    converted = {}
    for pair_symbol, pair_data in data.items():
        # Если это старый формат (есть 'position' но нет 'positions')
        if 'position' in pair_data and 'positions' not in pair_data:
            # Конвертируем в новый формат
            if pair_data.get('position') == 'long' and pair_data.get('position_size_usdt', 0) > 0:
                entry_price = pair_data.get('entry_price', 0)
                position_size = pair_data.get('position_size_usdt', 0)
                converted[pair_symbol] = {
                    'positions': [{
                        'id': 'legacy_auto',
                        'entry_price': entry_price,
                        'position_size_usdt': position_size,
                        'amount_crypto': position_size / entry_price if entry_price > 0 else 0,
                        'opened_at': pair_data.get('opened_at', 0),
                        'order_id': None,
                        'is_legacy': True,
                        'note': 'Авто-конвертировано из старого формата'
                    }],
                    'total_position_size_usdt': position_size,
                    'average_entry_price': entry_price,
                    'max_entry_price': entry_price,
                    'total_amount_crypto': position_size / entry_price if entry_price > 0 else 0,
                    'next_position_id': 2
                }
            else:
                # Позиция закрыта
                converted[pair_symbol] = {
                    'positions': [],
                    'total_position_size_usdt': 0,
                    'average_entry_price': 0,
                    'max_entry_price': 0,
                    'total_amount_crypto': 0,
                    'next_position_id': 1
                }
        else:
            # Уже новый формат
            converted[pair_symbol] = pair_data
    
    return converted

def add_position(pair_symbol, entry_price, position_size_usdt, amount_crypto, order_id=None, file_path='position_state.json'):
    """Добавляет новую позицию для пары"""
    state = load_position_state(file_path)
    
    if pair_symbol not in state:
        state[pair_symbol] = {
            'positions': [],
            'total_position_size_usdt': 0,
            'average_entry_price': 0,
            'max_entry_price': 0,
            'total_amount_crypto': 0,
            'next_position_id': 1
        }
    
    pair_data = state[pair_symbol]
    next_id = pair_data.get('next_position_id', 1)
    
    # Создаем новую позицию
    new_position = {
        'id': next_id,
        'entry_price': entry_price,
        'position_size_usdt': position_size_usdt,
        'amount_crypto': amount_crypto,
        'opened_at': int(datetime.now().timestamp() * 1000),
        'order_id': order_id,
        'is_legacy': False,
        'note': ''
    }
    
    # Добавляем в массив
    pair_data['positions'].append(new_position)
    pair_data['next_position_id'] = next_id + 1
    
    # Пересчитываем итоги
    pair_data['total_position_size_usdt'] = sum(p['position_size_usdt'] for p in pair_data['positions'])
    pair_data['total_amount_crypto'] = sum(p['amount_crypto'] for p in pair_data['positions'])
    
    if pair_data['positions']:
        total_cost = pair_data['total_position_size_usdt']
        total_amount = pair_data['total_amount_crypto']
        pair_data['average_entry_price'] = total_cost / total_amount if total_amount > 0 else 0
        pair_data['max_entry_price'] = max(p['entry_price'] for p in pair_data['positions'])
    
    # Сохраняем
    with open(file_path, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    return new_position

def close_all_positions(pair_symbol, file_path='position_state.json'):
    """Закрывает все позиции для пары"""
    state = load_position_state(file_path)
    
    if pair_symbol in state:
        state[pair_symbol] = {
            'positions': [],
            'total_position_size_usdt': 0,
            'average_entry_price': 0,
            'max_entry_price': 0,
            'total_amount_crypto': 0,
            'next_position_id': state[pair_symbol].get('next_position_id', 1)
        }
        
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    return True

def get_positions_count(pair_symbol, file_path='position_state.json'):
    """Возвращает количество открытых позиций для пары"""
    state = load_position_state(file_path)
    pair_data = state.get(pair_symbol, {})
    return len(pair_data.get('positions', []))

def get_total_position_size(pair_symbol, file_path='position_state.json'):
    """Возвращает общий размер позиции для пары"""
    state = load_position_state(file_path)
    pair_data = state.get(pair_symbol, {})
    return pair_data.get('total_position_size_usdt', 0)

def get_max_entry_price(pair_symbol, file_path='position_state.json'):
    """Возвращает максимальную цену входа для пары"""
    state = load_position_state(file_path)
    pair_data = state.get(pair_symbol, {})
    return pair_data.get('max_entry_price', 0)

if __name__ == '__main__':
    # Тест
    print("Тестирование функций...")
    state = load_position_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))
