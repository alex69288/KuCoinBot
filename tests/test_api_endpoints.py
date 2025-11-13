#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест API эндпоинтов в режиме разработки
"""
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Устанавливаем DEV_MODE
os.environ['DEV_MODE'] = '1'

async def test_api_endpoints():
    """Тест API эндпоинтов"""
    from httpx import AsyncClient
    
    print("🧪 Тестирование API эндпоинтов...")
    
    base_url = "http://127.0.0.1:8000"
    
    async with AsyncClient(base_url=base_url) as client:
        # Тест 1: /api/status
        print("\n📊 Тест 1: /api/status")
        try:
            response = await client.get("/api/status?init_data=debug_mode")
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Получены данные: positions={data.get('positions', {}).get('open_count', 0)} позиций")
            else:
                print(f"  ❌ Ошибка: {response.text}")
        except Exception as e:
            print(f"  ❌ Исключение: {e}")
        
        # Тест 2: /api/market
        print("\n📈 Тест 2: /api/market")
        try:
            response = await client.get("/api/market?init_data=debug_mode")
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Получены данные: {data.get('symbol', 'N/A')} = {data.get('current_price', 0):.2f} USDT")
            else:
                print(f"  ❌ Ошибка: {response.text}")
        except Exception as e:
            print(f"  ❌ Исключение: {e}")
        
        # Тест 3: /api/status с compact=1
        print("\n📊 Тест 3: /api/status?compact=1")
        try:
            response = await client.get("/api/status?init_data=debug_mode&compact=1")
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Компактный формат: {len(str(data))} байт")
            else:
                print(f"  ❌ Ошибка: {response.text}")
        except Exception as e:
            print(f"  ❌ Исключение: {e}")

if __name__ == '__main__':
    print("⚠️  Убедитесь, что бот запущен на порту 8000!")
    print("   Запустите: python main_dev.py")
    print()
    input("Нажмите Enter для продолжения...")
    
    asyncio.run(test_api_endpoints())
