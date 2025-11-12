"""
Тесты для задач 6 и 9: Настройки уведомлений и статистика за сегодня
"""
import sys
import os
from datetime import datetime, date

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_notification_settings_exist():
    """Проверка наличия настроек уведомлений в HTML"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие блока настроек уведомлений
    assert 'notification-settings' in content, "Блок настроек уведомлений не найден"
    
    # Проверяем наличие всех типов уведомлений
    assert 'notify-trades' in content, "Переключатель уведомлений о сделках не найден"
    assert 'notify-tp-approach' in content, "Переключатель уведомлений о приближении к TP не найден"
    assert 'notify-stop-loss' in content, "Переключатель уведомлений о стоп-лоссе не найден"
    assert 'notify-price-changes' in content, "Переключатель уведомлений об изменении цены не найден"
    assert 'notify-signals' in content, "Переключатель уведомлений о сигналах не найден"
    
    print("✓ Все настройки уведомлений присутствуют в HTML")

def test_today_statistics_exist():
    """Проверка наличия блока статистики за сегодня"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие блока "Сегодня"
    assert 'Сегодня' in content, "Заголовок 'Сегодня' не найден"
    assert 'today-trades' in content, "Поле 'today-trades' не найдено"
    assert 'today-pnl' in content, "Поле 'today-pnl' не найдено"
    assert 'today-win-rate' in content, "Поле 'today-win-rate' не найдено"
    assert 'today-best-trade' in content, "Поле 'today-best-trade' не найдено"
    
    print("✓ Блок статистики за сегодня присутствует в HTML")

def test_notification_functions_exist():
    """Проверка наличия функций для работы с уведомлениями"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие функций
    assert 'toggleNotifyTrades()' in content, "Функция toggleNotifyTrades не найдена"
    assert 'toggleNotifyTPApproach()' in content, "Функция toggleNotifyTPApproach не найдена"
    assert 'toggleNotifyStopLoss()' in content, "Функция toggleNotifyStopLoss не найдена"
    assert 'toggleNotifyPriceChanges()' in content, "Функция toggleNotifyPriceChanges не найдена"
    assert 'toggleNotifySignals()' in content, "Функция toggleNotifySignals не найдена"
    assert 'saveNotificationSettings()' in content, "Функция saveNotificationSettings не найдена"
    assert 'updateNotificationSettings(' in content, "Функция updateNotificationSettings не найдена"
    
    print("✓ Все функции для работы с уведомлениями присутствуют")

def test_trailing_stop_description():
    """Проверка наличия описания Trailing Stop"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие описания Trailing Stop
    assert 'Автоматическое перемещение стоп-лосса' in content or 'Trailing Stop' in content, \
        "Описание Trailing Stop не найдено"
    
    print("✓ Описание Trailing Stop добавлено")

def test_demo_mode_description():
    """Проверка наличия описания демо-режима"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие описания демо-режима
    assert 'демо' in content.lower() or 'тестовый режим' in content.lower(), \
        "Описание демо-режима не найдено"
    
    print("✓ Описание демо-режима добавлено")

def test_server_notification_endpoint():
    """Проверка наличия endpoint для настроек уведомлений"""
    with open('webapp/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие endpoint
    assert '/api/settings/notifications' in content, "Endpoint для настроек уведомлений не найден"
    assert 'NotificationSettingsUpdate' in content, "Модель NotificationSettingsUpdate не найдена"
    
    print("✓ API endpoint для настроек уведомлений присутствует")

def test_server_today_statistics():
    """Проверка наличия логики для статистики за сегодня в server.py"""
    with open('webapp/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие логики для сегодняшней статистики
    assert 'today' in content, "Логика для статистики за сегодня не найдена"
    assert 'date.today()' in content or 'datetime.now().date()' in content, \
        "Фильтрация по сегодняшней дате не найдена"
    
    print("✓ Логика для статистики за сегодня добавлена в server.py")

def test_analytics_loads_today_data():
    """Проверка загрузки данных за сегодня в функции loadAnalytics"""
    with open('webapp/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем обработку данных за сегодня
    assert "data.today" in content, "Обработка данных 'today' в loadAnalytics не найдена"
    
    print("✓ Функция loadAnalytics обрабатывает данные за сегодня")

if __name__ == '__main__':
    print("Запуск тестов для задач 6 и 9...\n")
    
    try:
        test_notification_settings_exist()
        test_today_statistics_exist()
        test_notification_functions_exist()
        test_trailing_stop_description()
        test_demo_mode_description()
        test_server_notification_endpoint()
        test_server_today_statistics()
        test_analytics_loads_today_data()
        
        print("\n" + "="*50)
        print("✅ Все тесты пройдены успешно!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Тест не пройден: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        sys.exit(1)
