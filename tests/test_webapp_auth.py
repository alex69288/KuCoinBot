#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест аутентификации WebApp в режиме разработки
"""
import os
import sys

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dev_mode_auth():
    """Тест пропуска аутентификации в DEV_MODE"""
    print("🧪 Тестирование аутентификации WebApp...")
    
    # Устанавливаем DEV_MODE
    os.environ['DEV_MODE'] = '1'
    
    from webapp.server import verify_telegram_webapp_data
    
    # Тест 1: Пустой init_data
    result1 = verify_telegram_webapp_data('', 'test_token')
    assert result1 == True, "❌ Пустой init_data должен проходить в DEV_MODE"
    print("✅ Тест 1: Пустой init_data проходит")
    
    # Тест 2: debug_mode
    result2 = verify_telegram_webapp_data('debug_mode', 'test_token')
    assert result2 == True, "❌ debug_mode должен проходить в DEV_MODE"
    print("✅ Тест 2: debug_mode проходит")
    
    # Тест 3: Любой init_data в DEV_MODE
    result3 = verify_telegram_webapp_data('any_data', 'test_token')
    assert result3 == True, "❌ Любой init_data должен проходить в DEV_MODE"
    print("✅ Тест 3: Произвольный init_data проходит")
    
    # Тест 4: Отключаем DEV_MODE
    os.environ['DEV_MODE'] = '0'
    result4 = verify_telegram_webapp_data('', 'test_token')
    assert result4 == False, "❌ Пустой init_data НЕ должен проходить в production режиме"
    print("✅ Тест 4: Пустой init_data блокируется в production")
    
    print("\n✅ Все тесты аутентификации прошли успешно!")

if __name__ == '__main__':
    test_dev_mode_auth()
