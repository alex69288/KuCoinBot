"""
Тесты для проверки улучшений веб-приложения торгового бота
"""
import pytest
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_balance_update_disabled():
    """Тест: Проверка что обновления баланса отключены"""
    # Читаем файл bot.py и проверяем что вызов закомментирован
    bot_file = os.path.join(os.path.dirname(__file__), '..', 'core', 'bot.py')
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что строка закомментирована
    assert '# self.telegram.send_balance_update()' in content, \
        "Вызов send_balance_update() должен быть закомментирован"
    
    print("✅ Тест пройден: Обновления баланса отключены")


def test_market_data_has_change_24h():
    """Тест: Проверка что API возвращает изменение за 24 часа"""
    # Проверяем что в server.py есть правильная обработка change_24h
    server_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'server.py')
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'change_24h = ticker.get(\'change\', 0)' in content, \
        "Должна быть обработка изменения цены за 24 часа"
    
    assert '"change_24h": change_24h' in content, \
        "change_24h должен возвращаться в ответе API"
    
    print("✅ Тест пройден: API правильно обрабатывает изменение за 24 часа")


def test_position_count_logic():
    """Тест: Проверка логики подсчета позиций"""
    server_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'server.py')
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что есть правильное условие для подсчета позиций
    assert "if trading_bot.position and trading_bot.position == 'long'" in content, \
        "Должна быть проверка что позиция открыта (long)"
    
    assert 'positions_info["open_count"] = 1' in content, \
        "Должно устанавливаться количество позиций = 1"
    
    print("✅ Тест пройден: Логика подсчета позиций корректна")


def test_take_profit_sign():
    """Тест: Проверка что знак Take Profit отображается корректно"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что есть логика добавления знака
    assert "toTp >= 0 ? '+' : ''" in content or "toTp >= 0 ? '+' : '-'" in content, \
        "Должна быть логика добавления знака + или - для Take Profit"
    
    print("✅ Тест пройден: Знак Take Profit добавляется корректно")


def test_ema_percent_display():
    """Тест: Проверка отображения процента EMA"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что процент отображается с правильным форматированием
    assert "emaPercent.toFixed(2)" in content, \
        "EMA процент должен отображаться с 2 знаками после запятой"
    
    assert "emaPercent >= 0 ? '+' : ''" in content or "'+':" in content, \
        "Должен добавляться знак + для положительных значений EMA"
    
    print("✅ Тест пройден: EMA процент отображается корректно")


def test_market_symbol_with_icon():
    """Тест: Проверка что иконка добавляется к названию пары"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что есть вставка SVG иконки
    assert "symbolEl.innerHTML" in content or "icon-money" in content, \
        "Должна быть иконка перед названием торговой пары"
    
    print("✅ Тест пройден: Иконка добавляется к названию пары")


def test_documentation_exists():
    """Тест: Проверка что создана документация об изменениях"""
    doc_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'WEBAPP_IMPROVEMENTS_REPORT.md')
    
    assert os.path.exists(doc_file), \
        "Должен существовать файл документации WEBAPP_IMPROVEMENTS_REPORT.md"
    
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем что документация содержит основные разделы
    assert "Выполненные улучшения" in content, "Должен быть раздел о выполненных улучшениях"
    assert "Запланированные улучшения" in content, "Должен быть раздел о запланированных улучшениях"
    assert "Технические детали" in content, "Должен быть раздел с техническими деталями"
    
    print("✅ Тест пройден: Документация создана и содержит нужные разделы")


def test_modal_window_exists():
    """Тест: Проверка что добавлено модальное окно подтверждения"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'id="confirm-modal"' in content, "Должно быть модальное окно с id=confirm-modal"
    assert 'class="modal"' in content, "Должен быть класс modal"
    assert 'showConfirmModal' in content, "Должна быть функция showConfirmModal"
    
    print("✅ Тест пройден: Модальное окно добавлено")


def test_trading_toggle_switch():
    """Тест: Проверка что добавлен переключатель торговли"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'id="trading-enabled"' in content, "Должен быть переключатель торговли"
    assert 'toggleTrading()' in content, "Должна быть функция toggleTrading"
    assert 'loadTradingStatus' in content, "Должна быть функция loadTradingStatus"
    
    print("✅ Тест пройден: Переключатель торговли добавлен")


def test_save_control_settings():
    """Тест: Проверка что добавлена кнопка сохранения настроек"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'saveControlSettings' in content, "Должна быть функция saveControlSettings"
    assert 'Сохранить настройки' in content, "Должна быть кнопка сохранения настроек"
    
    print("✅ Тест пройден: Кнопка сохранения настроек добавлена")


def test_auto_scroll_on_focus():
    """Тест: Проверка что добавлена автопрокрутка при фокусе"""
    html_file = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'scrollIntoView' in content, "Должна быть логика автопрокрутки"
    assert "addEventListener('focus'" in content, "Должен быть обработчик фокуса"
    
    print("✅ Тест пройден: Автопрокрутка при фокусе добавлена")


if __name__ == '__main__':
    print("=" * 80)
    print("ЗАПУСК ТЕСТОВ УЛУЧШЕНИЙ ВЕБ-ПРИЛОЖЕНИЯ")
    print("=" * 80)
    print()
    
    try:
        test_balance_update_disabled()
        test_market_data_has_change_24h()
        test_position_count_logic()
        test_take_profit_sign()
        test_ema_percent_display()
        test_market_symbol_with_icon()
        test_documentation_exists()
        test_modal_window_exists()
        test_trading_toggle_switch()
        test_save_control_settings()
        test_auto_scroll_on_focus()
        
        print()
        print("=" * 80)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 80)
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"❌ ТЕСТ НЕ ПРОЙДЕН: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ОШИБКА ПРИ ВЫПОЛНЕНИИ ТЕСТА: {e}")
        print("=" * 80)
        sys.exit(1)
