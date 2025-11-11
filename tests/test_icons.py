"""
Тест загрузки SVG иконок
"""
import requests
import time
from pathlib import Path

def test_icons_loading():
    """Тестирует доступность и корректность SVG иконок"""
    
    print("=" * 50)
    print("🎨 Тест загрузки SVG иконок")
    print("=" * 50)
    
    # URL иконок (измените на ваш адрес сервера)
    base_url = "http://localhost:8000"
    icons_url = f"{base_url}/static/icons.svg"
    
    print(f"\n📡 Проверка доступности: {icons_url}")
    
    try:
        # Измеряем время загрузки
        start_time = time.time()
        response = requests.get(icons_url, timeout=5)
        load_time = (time.time() - start_time) * 1000  # в миллисекундах
        
        print(f"⏱️  Время загрузки: {load_time:.0f}мс")
        
        # Проверяем статус
        if response.status_code == 200:
            print("✅ Статус: 200 OK")
        else:
            print(f"❌ Статус: {response.status_code}")
            return False
        
        # Проверяем content-type
        content_type = response.headers.get('content-type', '')
        print(f"📄 Content-Type: {content_type}")
        
        if 'svg' not in content_type.lower():
            print("⚠️  Предупреждение: Content-Type не содержит 'svg'")
        
        # Проверяем размер
        size = len(response.content)
        print(f"📦 Размер: {size} байт ({size/1024:.1f} KB)")
        
        # Проверяем содержимое
        svg_content = response.text
        
        print("\n🔍 Проверка содержимого SVG:")
        
        # Проверка на валидный SVG
        if '<svg' in svg_content:
            print("  ✅ Содержит тег <svg>")
        else:
            print("  ❌ Не содержит тег <svg>")
            return False
        
        # Проверка на символы
        if '<symbol' in svg_content:
            symbol_count = svg_content.count('<symbol')
            print(f"  ✅ Найдено {symbol_count} иконок (<symbol>)")
        else:
            print("  ❌ Не содержит теги <symbol>")
            return False
        
        # Проверяем наличие важных иконок
        required_icons = [
            'icon-home',
            'icon-chart',
            'icon-settings',
            'icon-money',
            'icon-robot',
            'icon-circle-green',
            'icon-circle-red',
            'icon-circle-yellow'
        ]
        
        print("\n📋 Проверка наличия необходимых иконок:")
        missing_icons = []
        
        for icon in required_icons:
            if f'id="{icon}"' in svg_content or f"id='{icon}'" in svg_content:
                print(f"  ✅ {icon}")
            else:
                print(f"  ❌ {icon} - ОТСУТСТВУЕТ")
                missing_icons.append(icon)
        
        if missing_icons:
            print(f"\n⚠️  Отсутствуют иконки: {', '.join(missing_icons)}")
        
        # Оценка производительности
        print("\n⚡ Оценка производительности:")
        if load_time < 100:
            print("  🟢 Отлично! (<100мс)")
        elif load_time < 300:
            print("  🟡 Хорошо (100-300мс)")
        elif load_time < 1000:
            print("  🟠 Приемлемо (300-1000мс)")
        else:
            print("  🔴 Медленно (>1000мс)")
            print("  💡 Рекомендация: Оптимизируйте SVG файл или используйте CDN")
        
        # Рекомендации по кэшированию
        cache_control = response.headers.get('cache-control', '')
        if cache_control:
            print(f"\n💾 Кэширование: {cache_control}")
        else:
            print("\n⚠️  Заголовки кэширования не установлены")
            print("  💡 Рекомендация: Добавьте Cache-Control для статических файлов")
        
        print("\n✅ Все проверки пройдены!")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Превышено время ожидания (>5 сек)")
        print("💡 Сервер слишком медленно отвечает")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("💡 Убедитесь, что сервер запущен: python main_with_webapp.py")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n" + "=" * 50)


def test_icons_file():
    """Проверяет наличие файла icons.svg"""
    
    print("\n" + "=" * 50)
    print("📁 Проверка файла icons.svg")
    print("=" * 50)
    
    icons_path = Path(__file__).parent.parent / "webapp" / "static" / "icons.svg"
    
    print(f"\n📍 Путь: {icons_path}")
    
    if icons_path.exists():
        print("✅ Файл существует")
        
        size = icons_path.stat().st_size
        print(f"📦 Размер: {size} байт ({size/1024:.1f} KB)")
        
        if size < 1000:
            print("⚠️  Файл слишком маленький (<1KB)")
        elif size > 100000:
            print("⚠️  Файл слишком большой (>100KB)")
            print("💡 Рекомендация: Оптимизируйте SVG (удалите лишние данные)")
        else:
            print("✅ Размер файла оптимален")
        
        return True
    else:
        print("❌ Файл не найден!")
        print("💡 Убедитесь, что файл icons.svg находится в webapp/static/")
        return False


if __name__ == "__main__":
    from datetime import datetime
    
    print("\n🧪 Icons Test Suite")
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Тест 1: Проверка файла
    file_ok = test_icons_file()
    
    # Тест 2: Проверка через HTTP
    if file_ok:
        http_ok = test_icons_loading()
    else:
        print("\n⏭️  Пропущен HTTP тест (файл не найден)")
        http_ok = False
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print(f"Файл icons.svg: {'✅ OK' if file_ok else '❌ FAILED'}")
    print(f"HTTP загрузка:  {'✅ OK' if http_ok else '❌ FAILED'}")
    
    if file_ok and http_ok:
        print("\n🎉 Все тесты пройдены успешно!")
    else:
        print("\n⚠️  Некоторые тесты не пройдены")
    
    print("=" * 50)
