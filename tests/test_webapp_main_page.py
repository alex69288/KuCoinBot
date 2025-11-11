"""
Тест главной страницы webapp с полной информацией
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_html_structure():
    """Проверяем структуру HTML файла"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp', 'static', 'index.html')
    
    print("🔍 Проверка структуры HTML файла...")
    
    if not os.path.exists(html_path):
        print(f"❌ Файл не найден: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие всех необходимых элементов
    required_elements = [
        # Обновление рынка
        'ОБНОВЛЕНИЕ РЫНКА',
        'market-symbol',
        'market-price',
        'market-change-24h',
        'market-ema',
        'market-signal',
        'market-ml',
        
        # Позиция
        'ПОЗИЦИЯ ОТКРЫТА',
        'position-count',
        'position-size',
        'position-entry-price',
        'position-current-profit',
        'position-to-tp',
        'position-tp-target',
        'position-fees'
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        print(f"❌ Отсутствуют элементы: {', '.join(missing)}")
        return False
    
    print("✅ Все необходимые элементы присутствуют в HTML")
    return True


def test_api_endpoints():
    """Проверяем наличие правильных API endpoints в server.py"""
    server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp', 'server.py')
    
    print("\n🔍 Проверка API endpoints...")
    
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, что endpoints возвращают правильные данные
    checks = [
        ('positions_info', 'API /api/status должен возвращать positions_info'),
        ('ema_info', 'API /api/market должен возвращать ema_info'),
        ('ml_info', 'API /api/market должен возвращать ml_info'),
        ('"signal":', 'API /api/market должен возвращать signal')
    ]
    
    for check, description in checks:
        if check not in content:
            print(f"❌ {description}")
            return False
        else:
            print(f"✅ {description}")
    
    return True


def test_javascript_functions():
    """Проверяем JavaScript функции для загрузки данных"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp', 'static', 'index.html')
    
    print("\n🔍 Проверка JavaScript функций...")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_js = [
        'loadStatus',
        'loadMarket',
        'position-count',
        'position-size',
        'position-entry-price',
        'position-current-profit',
        'market-ema',
        'market-signal',
        'market-ml'
    ]
    
    missing = []
    for js_element in required_js:
        if js_element not in content:
            missing.append(js_element)
    
    if missing:
        print(f"❌ Отсутствуют JS элементы: {', '.join(missing)}")
        return False
    
    print("✅ Все необходимые JavaScript элементы присутствуют")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Тестирование главной страницы webapp")
    print("=" * 60)
    
    results = []
    
    # Тест 1: Структура HTML
    results.append(test_html_structure())
    
    # Тест 2: API endpoints
    results.append(test_api_endpoints())
    
    # Тест 3: JavaScript функции
    results.append(test_javascript_functions())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("=" * 60)
        sys.exit(1)
