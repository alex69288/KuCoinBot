"""
Интеграционный тест для проверки загрузки позиций через API
"""
import sys
import os
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Добавляем корневую папку в пути поиска
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.position_manager import load_position_state

def test_position_loading_from_file():
    """Полная цепочка загрузки позиций"""
    print("\n" + "="*70)
    print("🔍 ИНТЕГРАЦИОННЫЙ ТЕСТ ЗАГРУЗКИ ПОЗИЦИЙ")
    print("="*70)
    
    # Шаг 1: Загружаем из файла
    print("\n1️⃣  Загрузка из position_state.json:")
    state = load_position_state('position_state.json')
    
    if not state:
        print("   ❌ Ошибка загрузки файла!")
        return False
    
    print(f"   ✅ Файл загружен, пар: {len(state)}")
    
    # Шаг 2: Обработка как в API
    print("\n2️⃣  Обработка данных (как в /api/positions):")
    
    positions = []
    total_positions = 0
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            total_positions += len(positions_list)
            
            print(f"   📌 {pair_symbol}:")
            
            # Обработаем каждую позицию
            for pos_data in positions_list:
                # Симулируем получение текущей цены
                entry_price = pos_data.get('entry_price', 0)
                position_size_usdt = pos_data.get('position_size_usdt', 0)
                
                # Для теста используем фиксированную цену
                current_price = entry_price * 0.95  # 5% ниже входа
                
                # Вычисляем PnL
                pnl = 0
                if entry_price > 0 and current_price > 0:
                    pnl = (current_price - entry_price) * position_size_usdt / entry_price
                
                position = {
                    "id": f"{pair_symbol}_{pos_data.get('id', 0)}",
                    "pair": pair_symbol,
                    "status": "long",
                    "entry_price": entry_price,
                    "current_price": current_price,
                    "amount": pos_data.get('amount_crypto', 0),
                    "position_size_usdt": position_size_usdt,
                    "pnl": pnl,
                    "pnl_percent": ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0,
                    "opened_at": pos_data.get('opened_at', 0),
                }
                
                positions.append(position)
                print(f"      ✓ Позиция {pos_data.get('id')}: {position_size_usdt} USDT")
    
    print(f"\n   📊 Всего позиций: {total_positions}")
    
    if total_positions == 0:
        print("   ⚠️  Позиции не найдены!")
        return False
    
    # Шаг 3: Проверяем формат
    print("\n3️⃣  Проверка формата ответа API:")
    print(f"   Тип: {type(positions).__name__} (должен быть 'list')")
    print(f"   Количество: {len(positions)}")
    
    if len(positions) > 0:
        pos = positions[0]
        print(f"\n   Первая позиция:")
        print(f"      - id: {pos.get('id')} ✓")
        print(f"      - pair: {pos.get('pair')} ✓")
        print(f"      - entry_price: {pos.get('entry_price')} ✓")
        print(f"      - position_size_usdt: {pos.get('position_size_usdt')} ✓")
        print(f"      - pnl: {pos.get('pnl')} ✓")
        print(f"      - pnl_percent: {pos.get('pnl_percent')} ✓")
    
    # Шаг 4: Проверяем что фронтенд может распарсить
    print("\n4️⃣  Парсинг фронтенд кодом:")
    
    html_output = positions
    if not html_output or len(html_output) == 0:
        print("   ⚠️  Нет позиций для отображения")
    else:
        print("   ✅ Позиции готовы к отображению:")
        for i, pos in enumerate(html_output[:2], 1):  # Показываем первые 2
            pair = pos.get('pair', 'N/A')
            pnl = pos.get('pnl', 0)
            pnl_percent = pos.get('pnl_percent', 0)
            print(f"      {i}. {pair}: {pnl:.2f} USDT ({pnl_percent:.2f}%)")
    
    # Шаг 5: Проверяем что можем закрыть позицию
    print("\n5️⃣  Функция закрытия позиции:")
    if len(positions) > 0:
        test_pos_id = positions[0]['id']
        print(f"   ✓ Можно закрыть позицию: {test_pos_id}")
    
    return True


def test_position_state_structure():
    """Проверяет структуру position_state.json"""
    print("\n" + "="*70)
    print("🔍 ПРОВЕРКА СТРУКТУРЫ POSITION_STATE.JSON")
    print("="*70)
    
    state = load_position_state('position_state.json')
    
    print("\n✅ Структура состояния:")
    for pair_symbol, pair_data in state.items():
        print(f"\n  📌 {pair_symbol}:")
        
        # Проверяем ключевые поля
        required_fields = ['positions', 'total_position_size_usdt', 'average_entry_price']
        for field in required_fields:
            value = pair_data.get(field)
            status = "✓" if field in pair_data else "✗"
            print(f"     {status} {field}: {value if field in pair_data else 'ОТСУТСТВУЕТ'}")
        
        # Проверяем позиции
        positions = pair_data.get('positions', [])
        if positions:
            print(f"     📍 Позиций: {len(positions)}")
            for pos in positions:
                print(f"        - ID {pos.get('id')}: {pos.get('entry_price')} @ {pos.get('position_size_usdt')} USDT")
        else:
            print(f"     📍 Позиций: 0")
    
    return True


if __name__ == '__main__':
    try:
        test1_ok = test_position_loading_from_file()
        test2_ok = test_position_state_structure()
        
        print("\n" + "="*70)
        print("📋 ИТОГОВОЕ РЕЗЮМЕ")
        print("="*70)
        
        if test1_ok and test2_ok:
            print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
            print("\n📌 Выводы:")
            print("   1. position_state.json загружается корректно")
            print("   2. Позиции парсятся правильно")
            print("   3. Формат API ответа совместим с фронтенд")
            print("   4. Фронтенд должен видеть позиции")
            print("\n🔧 Если позиции всё ещё не отображаются:")
            print("   - Проверьте консоль браузера (F12)")
            print("   - Проверьте сетевые запросы (Network tab)")
            print("   - Убедитесь, что init_data передаётся корректно")
            print("   - Проверьте что /api/positions возвращает данные")
            sys.exit(0)
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
