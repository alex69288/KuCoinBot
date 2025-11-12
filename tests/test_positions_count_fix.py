"""
Тест для проверки исправления количества открытых позиций
Проверяем, что position_state.json правильно считается при разных рабочих директориях
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Добавляем корневую директорию в путь
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.position_manager import load_position_state


def test_position_count_with_absolute_path():
    """Тест подсчета позиций с абсолютным путем"""
    
    # Загружаем текущий файл состояния
    position_state_path = os.path.join(PROJECT_ROOT, 'position_state.json')
    
    print(f"📂 Проверяем файл: {position_state_path}")
    print(f"✅ Файл существует: {os.path.exists(position_state_path)}")
    
    if not os.path.exists(position_state_path):
        print("❌ ОШИБКА: Файл position_state.json не найден!")
        return False
    
    # Загружаем состояние
    state = load_position_state(position_state_path)
    
    print(f"\n📊 Содержимое файла состояния:")
    print(json.dumps(state, indent=2, ensure_ascii=False))
    
    # Подсчитываем общее количество позиций (как в server.py)
    total_open_positions = 0
    total_position_size_usdt = 0
    
    for pair_symbol, pair_data in state.items():
        if isinstance(pair_data, dict) and 'positions' in pair_data:
            positions_list = pair_data.get('positions', [])
            pair_count = len(positions_list)
            pair_size = pair_data.get('total_position_size_usdt', 0)
            
            print(f"\n🔹 {pair_symbol}:")
            print(f"   - Количество позиций: {pair_count}")
            print(f"   - Размер в USDT: {pair_size}")
            
            for pos in positions_list:
                print(f"   - Позиция #{pos.get('id')}: {pos.get('entry_price')} (размер: {pos.get('position_size_usdt')} USDT)")
            
            total_open_positions += pair_count
            total_position_size_usdt += pair_size
    
    print(f"\n💰 ИТОГО:")
    print(f"   - Всего открытых позиций: {total_open_positions}")
    print(f"   - Всего размер в USDT: {total_position_size_usdt}")
    
    # Проверяем результаты
    if total_open_positions == 2:
        print("\n✅ УСПЕХ! Количество позиций = 2 (как на сайте)")
        return True
    else:
        print(f"\n❌ ОШИБКА! Количество позиций = {total_open_positions}, ожидалось = 2")
        return False


def test_relative_vs_absolute_path():
    """Тест проверки работы с относительными и абсолютными путями"""
    
    print("\n" + "="*60)
    print("🧪 ТЕСТ: Относительный vs Абсолютный путь")
    print("="*60)
    
    # Сохраняем текущую рабочую директорию
    original_cwd = os.getcwd()
    
    try:
        # Переходим в другую директорию
        temp_dir = tempfile.gettempdir()
        os.chdir(temp_dir)
        print(f"📂 Изменили рабочую директорию на: {os.getcwd()}")
        
        # Пытаемся загрузить файл с относительным путем (должно СБОЙ)
        print(f"\n🔴 Попытка загрузить с относительным путем 'position_state.json'...")
        relative_exists = os.path.exists('position_state.json')
        print(f"   Результат: Файл {'найден' if relative_exists else 'НЕ найден'} ❌")
        
        # Пытаемся загрузить файл с абсолютным путем (должно работать)
        absolute_path = os.path.join(PROJECT_ROOT, 'position_state.json')
        print(f"\n🟢 Попытка загрузить с абсолютным путем: {absolute_path}...")
        absolute_exists = os.path.exists(absolute_path)
        print(f"   Результат: Файл {'найден' if absolute_exists else 'НЕ найден'} {'✅' if absolute_exists else '❌'}")
        
        if absolute_exists:
            state = load_position_state(absolute_path)
            total_positions = 0
            for pair_symbol, pair_data in state.items():
                if isinstance(pair_data, dict) and 'positions' in pair_data:
                    total_positions += len(pair_data.get('positions', []))
            print(f"   Всего позиций: {total_positions}")
        
        return absolute_exists
    
    finally:
        # Возвращаемся в оригинальную директорию
        os.chdir(original_cwd)
        print(f"\n📂 Вернулись в оригинальную директорию: {os.getcwd()}")


if __name__ == '__main__':
    print("🔍 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ КОЛИЧЕСТВА ПОЗИЦИЙ")
    print("="*60)
    
    # Тест 1: Проверка подсчета позиций
    test1_passed = test_position_count_with_absolute_path()
    
    # Тест 2: Проверка работы с абсолютными путями
    test2_passed = test_relative_vs_absolute_path()
    
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print("="*60)
    print(f"✅ Тест 1 (подсчет позиций): {'ПРОЙДЕН' if test1_passed else 'ПРОВАЛЕН'}")
    print(f"✅ Тест 2 (абсолютные пути): {'ПРОЙДЕН' if test2_passed else 'ПРОВАЛЕН'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Исправление работает корректно.")
        sys.exit(0)
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ. Требуется доработка.")
        sys.exit(1)
