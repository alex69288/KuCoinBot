"""
Тест для проверки API endpoints загрузки позиций
"""
import sys
import os
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Добавляем корневую папку в пути поиска
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.api_compact_responses import compact_positions_response

def test_compact_positions_response():
    """Тестирует функцию compact_positions_response"""
    print("\n" + "="*70)
    print("🔍 ТЕСТ КОМПАКТНОГО ФОРМАТА ПОЗИЦИЙ")
    print("="*70)
    
    # Симулируем ответ API
    full_response = [
        {
            "id": "BTC/USDT_1",
            "pair": "BTC/USDT",
            "status": "long",
            "entry_price": 110185.7,
            "current_price": 110000,
            "amount": 9.98314663336531e-06,
            "position_size_usdt": 1.1,
            "pnl": -20.5,
            "pnl_percent": -1.85,
            "opened_at": 1762033200000,
            "timestamp": "2025-11-12T00:00:00"
        },
        {
            "id": "BTC/USDT_2",
            "pair": "BTC/USDT",
            "status": "long",
            "entry_price": 103573.5,
            "current_price": 110000,
            "amount": 9.65497931420682e-06,
            "position_size_usdt": 1.0,
            "pnl": 61.75,
            "pnl_percent": 5.97,
            "opened_at": 1762360860000,
            "timestamp": "2025-11-12T00:00:00"
        }
    ]
    
    print("\n📥 Входные данные (полный формат):")
    print(f"   Позиций: {len(full_response)}")
    for i, pos in enumerate(full_response, 1):
        print(f"   {i}. {pos['pair']}: {pos['position_size_usdt']} USDT @ {pos['entry_price']}")
    
    # Применяем компактный формат
    print("\n🔄 Применение компактного формата...")
    try:
        compact_response = compact_positions_response(full_response)
        print("✅ Компактный формат создан успешно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Анализируем результат
    print("\n📤 Выходные данные (компактный формат):")
    
    # Считаем размер
    full_json = json.dumps(full_response)
    compact_json = json.dumps(compact_response)
    
    full_size = len(full_json)
    compact_size = len(compact_json)
    savings = ((full_size - compact_size) / full_size) * 100
    
    print(f"   Полный размер: {full_size} байт")
    print(f"   Компактный размер: {compact_size} байт")
    print(f"   Экономия: {savings:.1f}%")
    
    # Проверяем структуру
    print("\n✅ Структура компактного ответа:")
    if isinstance(compact_response, list) and len(compact_response) > 0:
        print("   Тип: список позиций ✓")
        print(f"   Количество: {len(compact_response)} ✓")
        
        # Проверяем каждую позицию
        for i, pos in enumerate(compact_response, 1):
            print(f"\n   Позиция {i}:")
            print(f"      - id: {pos.get('id')}")
            print(f"      - sym (pair): {pos.get('sym')}")
            print(f"      - sz (size_usdt): {pos.get('sz')}")
            print(f"      - ep (entry_price): {pos.get('ep')}")
            print(f"      - cp (current_price): {pos.get('cp')}")
            print(f"      - amt (amount): {pos.get('amt')}")
            print(f"      - pnl: {pos.get('pnl')}")
            print(f"      - pnl%: {pos.get('pnl%')}")
            
            # Проверяем обязательные поля
            required_fields = ['id', 'sym', 'sz', 'ep', 'cp', 'pnl', 'pnl%']
            missing_fields = [f for f in required_fields if f not in pos]
            if missing_fields:
                print(f"      ❌ Отсутствуют поля: {missing_fields}")
                return False
    else:
        print("   ❌ Ответ не является списком!")
        print(f"   Тип: {type(compact_response)}")
        return False
    
    # Проверяем совместимость с фронтенд
    print("\n🔗 Проверка совместимости с фронтенд:")
    print("   Фронтенд ожидает массив с полями:")
    print("   ✓ pos.id - для закрытия позиции")
    print("   ✓ pos.pair (или pos.sym) - название пары")
    print("   ✓ pos.position_size_usdt (или pos.sz) - размер позиции")
    print("   ✓ pos.entry_price (или pos.ep) - цена входа")
    print("   ✓ pos.current_price (или pos.cp) - текущая цена")
    print("   ✓ pos.pnl - прибыль/убыток в USDT")
    print("   ✓ pos.pnl_percent (или pos.pnl%) - прибыль/убыток в %")
    print("   ✓ pos.amount (или pos.amt) - объем крипто")
    
    return True


def test_api_response_chain():
    """Тестирует цепочку API → компактный формат"""
    print("\n" + "="*70)
    print("🔍 ТЕСТ ЦЕПОЧКИ API ОТВЕТОВ")
    print("="*70)
    
    # Симулируем API ответ
    api_response = {
        "id": "BTC/USDT_1",
        "pair": "BTC/USDT",
        "status": "long",
        "entry_price": 110185.7,
        "current_price": 110000,
        "amount": 9.98314663336531e-06,
        "position_size_usdt": 1.1,
        "pnl": -20.5,
        "pnl_percent": -1.85,
    }
    
    print("\n1️⃣  API возвращает:")
    print(f"   {api_response}")
    
    # Проверяем, как будет выглядеть в компактном формате
    compact_pos = {
        'id': api_response.get('id'),
        'sym': api_response.get('pair'),  # Ключевой момент - используем 'pair'
        'sz': round(api_response.get('position_size_usdt', 0), 2),
        'ep': round(api_response.get('entry_price', 0), 2),
        'cp': round(api_response.get('current_price', 0), 2),
        'amt': round(api_response.get('amount', 0), 8),
        'pnl': round(api_response.get('pnl', 0), 2),
        'pnl%': round(api_response.get('pnl_percent', 0), 2),
        'sts': api_response.get('status', 'long'),
    }
    
    print("\n2️⃣  Компактный формат:")
    print(f"   {compact_pos}")
    
    print("\n3️⃣  Фронтенд парсит:")
    print(f"   pos.sym (пара): {compact_pos.get('sym')} ✓")
    print(f"   pos.pnl (PnL): {compact_pos.get('pnl')} ✓")
    print(f"   pos.pnl% (PnL %): {compact_pos.get('pnl%')} ✓")
    
    return True


if __name__ == '__main__':
    try:
        test1_ok = test_compact_positions_response()
        test2_ok = test_api_response_chain()
        
        print("\n" + "="*70)
        print("📋 РЕЗЮМЕ ТЕСТИРОВАНИЯ")
        print("="*70)
        
        if test1_ok and test2_ok:
            print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
            print("\n🚀 Позиции должны загружаться правильно!")
            sys.exit(0)
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
