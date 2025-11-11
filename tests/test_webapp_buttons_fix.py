"""
Тест для проверки исправления ошибки WebAppPopupParamInvalid
Проверяет, что сервер корректно запускается и отвечает на запросы
"""
import sys
import os
import time
import requests

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_running():
    """Проверка, что сервер запущен"""
    try:
        response = requests.get('http://localhost:8000/ping', timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'pong'
        print("✅ Сервер запущен и отвечает на запросы")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False


def test_root_endpoint():
    """Проверка, что главная страница возвращается"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        assert response.status_code == 200
        content = response.text
        assert 'Trading Bot' in content
        assert 'Telegram.WebApp' in content
        print("✅ Главная страница загружается корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки главной страницы: {e}")
        return False


def test_index_html_fixed():
    """Проверка, что в index.html используется исправленный код"""
    try:
        # Читаем файл index.html
        index_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'webapp', 'static', 'index.html'
        )
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, что используется showPopup
        assert 'tg.showPopup({' in content
        assert 'title:' in content
        assert 'message:' in content
        assert 'buttons:' in content
        
        # Проверяем, что старый метод не используется (в функциях startBot/stopBot)
        # Примечание: showAlert может быть в комментариях, поэтому проверяем контекст
        lines = content.split('\n')
        in_function = False
        for line in lines:
            if 'function startBot()' in line or 'function stopBot()' in line:
                in_function = True
            if in_function and 'tg.showAlert(' in line and '//' not in line:
                print(f"❌ Найден старый метод tg.showAlert: {line}")
                return False
            if in_function and '}' in line and line.strip() == '}':
                in_function = False
        
        print("✅ Код index.html исправлен корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки index.html: {e}")
        return False


def test_api_health():
    """Проверка health endpoint"""
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        print("✅ API health endpoint работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки API health: {e}")
        return False


def test_documentation_exists():
    """Проверка наличия документации"""
    try:
        docs = [
            'FIX_WEBAPP_BUTTONS.md',
            'FIX_WEBAPP_BUTTONS_SUMMARY.md'
        ]
        
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        for doc in docs:
            doc_path = os.path.join(base_path, doc)
            assert os.path.exists(doc_path), f"Документ {doc} не найден"
        
        print("✅ Вся документация создана")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки документации: {e}")
        return False


def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ WebAppPopupParamInvalid")
    print("=" * 60)
    print()
    
    tests = [
        ("Сервер запущен", test_server_running),
        ("Главная страница", test_root_endpoint),
        ("Исправленный код", test_index_html_fixed),
        ("API Health", test_api_health),
        ("Документация", test_documentation_exists),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Тест: {name}")
        print("-" * 60)
        result = test_func()
        results.append((name, result))
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print()
    print(f"Всего тестов: {total}")
    print(f"Успешно: {passed}")
    print(f"Провалено: {total - passed}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        return 1


if __name__ == "__main__":
    sys.exit(main())
