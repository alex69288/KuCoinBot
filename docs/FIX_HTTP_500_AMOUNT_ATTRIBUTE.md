# Исправление HTTP 500: AttributeError 'amount'

## Дата: 11 ноября 2025

## Проблема
При обращении к эндпоинту `/api/status` в Web App возникала ошибка:
```
ERROR - Ошибка получения статуса: 'AdvancedTradingBot' object has no attribute 'amount'
```

Это приводило к HTTP 500 Internal Server Error и невозможности отображения статуса бота в интерфейсе.

## Причина
В файле `webapp/server.py` (строка 212) использовался несуществующий атрибут `trading_bot.amount`:

```python
position_info = {
    "position": trading_bot.position,
    "entry_price": trading_bot.entry_price,
    "amount": trading_bot.amount  # ❌ Атрибут не существует
}
```

Однако в классе `AdvancedTradingBot` (файл `core/bot.py`) такого атрибута нет. Вместо него используется `current_position_size_usdt`:

```python
class AdvancedTradingBot:
    def __init__(self):
        # ...
        self.position = None
        self.entry_price = 0
        self.current_position_size_usdt = 0  # ✅ Правильный атрибут
```

## Решение
Заменили использование `trading_bot.amount` на `trading_bot.current_position_size_usdt`:

```python
position_info = {
    "position": trading_bot.position,
    "entry_price": trading_bot.entry_price,
    "amount": trading_bot.current_position_size_usdt  # ✅ Исправлено
}
```

## Измененные файлы
- `webapp/server.py` - строка 212

## Тестирование
Создан тест `tests/test_webapp_status_fix.py`, который проверяет:
1. Доступность всех необходимых атрибутов у бота
2. Соответствие атрибутов в коде класса `AdvancedTradingBot`

Результаты:
```
✅ Тест 1 (мок-объект): ПРОЙДЕН
✅ Тест 2 (реальный класс): ПРОЙДЕН
```

## Результат
✅ Исправление устраняет ошибку HTTP 500 при запросе статуса  
✅ Web App теперь корректно отображает информацию о позиции  
✅ Атрибут `amount` в API статуса теперь содержит размер позиции в USDT

## Рекомендации
При добавлении новых атрибутов в класс `AdvancedTradingBot`:
1. Убедитесь, что они инициализируются в `__init__`
2. Обновите соответствующие обращения в `webapp/server.py`
3. Добавьте тесты для проверки доступности новых атрибутов
