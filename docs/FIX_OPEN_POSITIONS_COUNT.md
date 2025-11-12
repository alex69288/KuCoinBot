---
title: Исправление количества открытых позиций
date: 2025-11-12
version: v0.1.7
---

# 🔧 Исправление: Правильный подсчет открытых позиций

## Проблема

В приложении отображалось **1 открытая позиция**, а на скриншоте из KuCoin было видно **2 открытые позиции** для BTC/USDT после последней продажи.

Это произошло потому, что:

1. **API endpoint `/api/positions`** возвращал только одну "текущую позицию" из `trading_bot.position`
2. **API endpoint `/api/status`** подсчитывал позиции как `open_count = 1`
3. **Frontend** считал позиции на основе этих неправильных данных
4. **position_state.json** хранит ВСЕ открытые позиции в новом формате (массив), но использовались неправильно

## Решение

### 1. ✅ Обновлён endpoint `/api/positions` (webapp/server.py)

**Было:**
```python
# Возвращал только одну текущую позицию
if trading_bot.position and trading_bot.position != 'none':
    positions.append({...})
```

**Стало:**
```python
# Возвращает ВСЕ позиции из position_state.json
for pair_symbol, pair_data in state.items():
    if isinstance(pair_data, dict) and 'positions' in pair_data:
        for pos_data in pair_data.get('positions', []):
            positions.append({...})
```

**Возвращаемый формат:**
```json
[
  {
    "id": "BTC/USDT_1",
    "pair": "BTC/USDT",
    "status": "long",
    "entry_price": 110185.7,
    "current_price": 111287.56,
    "amount": 9.98e-06,
    "position_size_usdt": 1.1,
    "pnl": 0.011,
    "pnl_percent": 1.0,
    "opened_at": 1762033200000
  },
  {
    "id": "BTC/USDT_2",
    "pair": "BTC/USDT",
    "status": "long",
    "entry_price": 103573.5,
    "current_price": 104609.24,
    "amount": 9.65e-06,
    "position_size_usdt": 1.0,
    "pnl": 0.01,
    "pnl_percent": 1.0,
    "opened_at": 1762360860000
  }
]
```

### 2. ✅ Обновлён endpoint `/api/status` (webapp/server.py)

**Было:**
```python
# Подсчитывал только если trading_bot.position == 'long'
positions_info["open_count"] = 1
```

**Стало:**
```python
# Подсчитывает ВСЕ позиции из position_state.json
for pair_symbol, pair_data in state.items():
    if isinstance(pair_data, dict) and 'positions' in pair_data:
        positions_list = pair_data.get('positions', [])
        total_open_positions += len(positions_list)
        
positions_info["open_count"] = total_open_positions
```

### 3. ✅ Обновлены методы закрытия позиций (webapp/server.py)

#### `/api/positions/{position_id}/close`
- Теперь корректно парсит ID позиции (формат: `PAIR_ID`)
- Находит конкретную позицию в массиве и продаёт её
- Обновляет и сохраняет position_state.json

#### `/api/positions/close-all`
- Проходит по всем парам
- Закрывает все позиции во всех парах
- Правильно обновляет данные по каждой паре

### 4. ✅ Обновлен frontend (webapp/static/index.html)

**JavaScript функция `loadPositions()`:**
```javascript
// Было: ожидал data.positions[...]
const data = await response.json();
container.innerHTML = data.positions.map(pos => `...`);

// Стало: работает с массивом напрямую
const positions = await response.json();
container.innerHTML = positions.map(pos => `...`);
```

**Отображаемые поля:**
- `pos.pair` (была: `pos.symbol`)
- `pos.position_size_usdt` (новое)
- `pos.pnl_percent` (новое)
- `pos.amount` (вывод крипто)

### 5. ✅ Исправлена кодировка position_state.json

Файл был в кодировке `latin-1`, что вызывало проблемы при чтении. Конвертирован в `UTF-8`.

Обновлена функция `load_position_state()` в `utils/position_manager.py` для поддержки разных кодировок.

## Результаты

### До исправления:
```
[Позиции] Открытые позиции: 1
[Status]  open_count: 1
[Fact]    BTC/USDT имеет 2 позиции в position_state.json ❌
```

### После исправления:
```
[Позиции] Открытые позиции: 2
  - BTC/USDT_1: 1.1 USDT @ 110185.7 (+1.0%)
  - BTC/USDT_2: 1.0 USDT @ 103573.5 (+1.0%)
[Status]  open_count: 2 ✅
[Fact]    BTC/USDT имеет 2 позиции в position_state.json ✅
```

## Тестирование

Запустить тест:
```bash
python tests/test_open_positions_fix.py
```

Результат:
```
✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
✅ Количество открытых позиций: 2
```

## Изменённые файлы

- ✅ `webapp/server.py` - обновлены 3 endpoint (`/api/positions`, `/api/status`, методы закрытия)
- ✅ `webapp/static/index.html` - обновлена функция `loadPositions()`
- ✅ `utils/position_manager.py` - добавлена поддержка разных кодировок
- ✅ `tests/test_open_positions_fix.py` - новый файл с тестами

## Совместимость

- ✅ Обратная совместимость с `trading_bot.position` (fallback если нет position_state.json)
- ✅ Поддержка старого формата position_state.json (автоматическая конвертация)
- ✅ Работает с одной и несколькими парами

## Знакомые проблемы

Если количество позиций всё ещё неправильное:

1. **Проверьте кодировку position_state.json:**
   ```bash
   python -c "import json; f=open('position_state.json','r',encoding='utf-8'); json.load(f); print('✅')"
   ```

2. **Проверьте структуру position_state.json:**
   ```bash
   python tests/test_open_positions_fix.py
   ```

3. **Очистите кэш браузера** (Ctrl+Shift+Delete)

4. **Перезагрузите приложение**
