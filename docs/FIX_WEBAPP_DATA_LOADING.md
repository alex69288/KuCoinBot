# Исправление загрузки данных WebApp v1.3.2

## Проблема
WebApp показывал ошибку "Ошибка загрузки данных" несмотря на то, что API возвращал HTTP 200 OK.

## Причина
Несоответствие названий полей между API и frontend:

### API возвращал (старые названия):
- `is_running` вместо `trading_enabled`
- `price_change_24h` вместо `change_24h`
- `balance` как объект `{total_usdt: ..., free: ..., used: ...}`
- `position` как объект `{position: "long", entry_price: ..., amount: ...}`

### Frontend ожидал:
- `data.trading_enabled`
- `data.change_24h`
- `data.balance` как число
- `data.position` как строку
- `data.pnl` как число

## Решение

### 1. Изменения в `webapp/server.py`

#### Endpoint `/api/status` (строка ~190):
```python
# БЫЛО:
return {
    "is_running": trading_bot.is_running,
    "balance": balance,  # объект
    "position": position,  # объект
    ...
}

# СТАЛО:
return {
    "trading_enabled": getattr(trading_bot.settings.settings, 'trading_enabled', False),
    "balance": balance.get('total_usdt', 0.0) if balance else 0.0,  # число
    "position": position_text,  # строка "Long @ 104439.30 USDT"
    "pnl": pnl,  # добавлено
    ...
}
```

#### Endpoint `/api/market` (строка ~244):
```python
# БЫЛО:
return {
    "price_change_24h": ticker.get('change', 0),
    ...
}

# СТАЛО:
return {
    "change_24h": ticker.get('change', 0),
    ...
}
```

### 2. Изменения в `webapp/static/index.html`

#### Обработка balance (обратная совместимость):
```javascript
// Поддержка обоих форматов
const balance = typeof data.balance === 'number' 
    ? data.balance 
    : (data.balance?.total_usdt || 0);
```

#### Улучшенная обработка ошибок:
```javascript
// Проверка HTTP статуса
if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
}

// Подробное логирование типов данных
console.log('📊 Тип данных:', {
    trading_enabled: typeof data.trading_enabled,
    balance: typeof data.balance,
    position: typeof data.position,
    pnl: typeof data.pnl
});
```

## Тестирование

### Создан тест `tests/test_api_fields.py`:
```bash
python tests/test_api_fields.py
```

**Результаты:**
```
✅ API поля: PASSED
✅ Frontend ожидания: PASSED
✅ Обработка balance: PASSED

🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
```

## Что исправлено

1. ✅ API теперь возвращает `trading_enabled` вместо `is_running`
2. ✅ API возвращает `change_24h` вместо `price_change_24h`
3. ✅ `balance` упрощен до числа (total_usdt)
4. ✅ `position` конвертирован в строку "Long @ 104439.30 USDT"
5. ✅ Добавлено поле `pnl` (P&L текущей позиции)
6. ✅ Frontend корректно обрабатывает все поля
7. ✅ Добавлена детальная обработка ошибок с логированием
8. ✅ Обратная совместимость для поля `balance`

## Проверка в production

После деплоя проверить в browser console Telegram WebApp:

```
✅ Должны появиться логи:
🚀 WebApp загружен
📊 Начало загрузки данных...
📡 Загрузка статуса...
📊 Статус получен: {trading_enabled: false, balance: 150.50, ...}
📈 Загрузка рынка...
📊 Рынок получен: {symbol: "BTC/USDT", change_24h: 2.5, ...}
✅ Данные загружены успешно

❌ НЕ должно быть:
- Ошибка загрузки данных
- Cannot read property 'toFixed' of undefined
- data.trading_enabled is undefined
```

## Изменённые файлы
- `webapp/server.py` - исправлены названия полей в API
- `webapp/static/index.html` - улучшена обработка ошибок и данных
- `tests/test_api_fields.py` - новый тест для проверки соответствия

## Версия
v1.3.2 - Исправление названий полей API для WebApp
