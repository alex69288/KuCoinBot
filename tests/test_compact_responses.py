"""
Тесты для компактных форматов API ответов v0.1.12

Проверяет, что компактные функции правильно обрабатывают как словари, так и списки
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from webapp.api_compact_responses import (
    compact_status_response,
    compact_history_response,
    compact_positions_response
)


def test_compact_history_response_with_list():
    """Тест: compact_history_response должна работать со списком напрямую"""
    history_list = [
        {
            'id': '1',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'price': 50000,
            'size': 0.1,
            'fee': 0.001,
            'timestamp': datetime.now().isoformat()
        },
        {
            'id': '2',
            'symbol': 'BTC/USDT',
            'side': 'sell',
            'price': 51000,
            'size': 0.1,
            'fee': 0.001,
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    # Должна работать со списком
    result = compact_history_response(history_list)
    
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert 'tr' in result, "Результат должен содержать 'tr'"
    assert 'count' in result, "Результат должен содержать 'count'"
    assert 'ts' in result, "Результат должен содержать 'ts'"
    assert result['count'] == 2, f"Ожидалось 2 сделки, получено {result['count']}"
    assert len(result['tr']) == 2, f"Ожидалось 2 элемента в 'tr', получено {len(result['tr'])}"
    
    print("✅ test_compact_history_response_with_list PASSED")


def test_compact_history_response_with_dict():
    """Тест: compact_history_response должна работать со словарём (обратная совместимость)"""
    history_dict = {
        'trades': [
            {
                'id': '1',
                'symbol': 'BTC/USDT',
                'side': 'buy',
                'price': 50000,
                'size': 0.1,
                'fee': 0.001,
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    
    # Должна работать со словарём
    result = compact_history_response(history_dict)
    
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert result['count'] == 1, f"Ожидалась 1 сделка, получено {result['count']}"
    
    print("✅ test_compact_history_response_with_dict PASSED")


def test_compact_positions_response_with_list():
    """Тест: compact_positions_response должна работать со списком напрямую"""
    positions_list = [
        {
            'id': 'pos_1',
            'pair': 'BTC/USDT',
            'symbol': 'BTC/USDT',
            'position_size_usdt': 1000,
            'entry_price': 50000,
            'current_price': 51000,
            'amount': 0.02,
            'pnl': 100,
            'pnl_percent': 10,
            'status': 'long'
        }
    ]
    
    # Должна работать со списком
    result = compact_positions_response(positions_list)
    
    assert isinstance(result, list), "Результат должен быть списком"
    assert len(result) == 1, f"Ожидалась 1 позиция, получено {len(result)}"
    assert result[0]['id'] == 'pos_1', "ID позиции должен совпадать"
    
    print("✅ test_compact_positions_response_with_list PASSED")


def test_compact_status_response_handles_list():
    """Тест: compact_status_response должна обрабатывать позиции как список"""
    status_dict = {
        'positions': [
            {
                'id': 'pos_1',
                'pair': 'BTC/USDT',
                'entry_price': 50000,
                'position_size_usdt': 1000
            }
        ]
    }
    
    # Должна работать со списком позиций
    result = compact_status_response(status_dict)
    
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert 'p' in result, "Результат должен содержать 'p'"
    
    print("✅ test_compact_status_response_handles_list PASSED")


def test_compact_status_response_handles_dict():
    """Тест: compact_status_response должна обрабатывать позиции как словарь"""
    status_dict = {
        'positions': {
            'open_count': 1,
            'size_usdt': 1000,
            'entry_price': 50000,
            'current_profit_percent': 10,
            'current_profit_usdt': 100,
            'to_take_profit': 0
        }
    }
    
    # Должна работать со словарём позиций
    result = compact_status_response(status_dict)
    
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert result['p']['c'] == 1, "Количество позиций должно быть 1"
    assert result['p']['s'] == 1000, "Размер позиции должен быть 1000"
    
    print("✅ test_compact_status_response_handles_dict PASSED")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ КОМПАКТНЫХ ФОРМАТОВ API v0.1.12")
    print("="*60 + "\n")
    
    try:
        test_compact_history_response_with_list()
        test_compact_history_response_with_dict()
        test_compact_positions_response_with_list()
        test_compact_status_response_handles_list()
        test_compact_status_response_handles_dict()
        
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
