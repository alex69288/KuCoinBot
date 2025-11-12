# Синхронизация обновления данных позиций с ценой v0.1.12

## Описание проблемы
При обновлении цены через WebSocket обновлялись только данные профита позиций, но не обновлялись сами числовые значения:
- Количество открытых позиций
- Размер ставки (USDT)
- Цена входа (TP)
- До Take Profit (%)

## Решение
Расширена функция `updateMarketData()` в `webapp/static/index.html` для одновременного обновления ВСЕХ данных позиций при поступлении рыночного обновления через WebSocket.

## Изменения

### 1. Расширены данные, отслеживаемые в `prevValues`
Добавлены новые свойства для сравнения предыдущих значений:
- `openCount` - количество открытых позиций
- `positionSize` - размер ставки в USDT
- `positionEntryPrice` - цена входа
- `toTakeProfit` - расстояние до take profit

### 2. Расширена функция `updateMarketData()`
Теперь функция обновляет следующие данные позиций одновременно с ценой:

#### Количество открытых позиций
```javascript
const openCount = data.positions.open_count || 0;
const countEl = document.getElementById('position-count');
if (openCount !== prevValues.openCount) {
  applyFlash(countEl, openCount > (prevValues.openCount || 0) ? 'up' : 'down');
  prevValues.openCount = openCount;
}
countEl.textContent = openCount;
```

#### Размер ставки
```javascript
const sizeUsdt = data.positions.size_usdt || 0;
const sizeEl = document.getElementById('position-size');
if (sizeUsdt !== prevValues.positionSize) {
  applyFlash(sizeEl, sizeUsdt > (prevValues.positionSize || 0) ? 'up' : 'down');
  prevValues.positionSize = sizeUsdt;
}
sizeEl.textContent = `${sizeUsdt.toFixed(2)} USDT`;
```

#### Цена входа
```javascript
const entryPrice = data.positions.entry_price || 0;
const entryEl = document.getElementById('position-entry-price');
if (entryPrice !== prevValues.positionEntryPrice) {
  applyFlash(entryEl, entryPrice > (prevValues.positionEntryPrice || 0) ? 'up' : 'down');
  prevValues.positionEntryPrice = entryPrice;
}
entryEl.textContent = `${entryPrice.toFixed(2)} USDT`;
```

#### До Take Profit
```javascript
const toTp = data.positions.to_take_profit || 0;
const toTpEl = document.getElementById('position-to-tp');
if (toTp !== prevValues.toTakeProfit) {
  applyFlash(toTpEl, toTp > (prevValues.toTakeProfit || 0) ? 'up' : 'down');
  prevValues.toTakeProfit = toTp;
}
toTpEl.textContent = `${toTp >= 0 ? '+' : ''}${toTp.toFixed(1)}%`;
```

## Преимущества

1. **Синхронизация в реальном времени**: Все числа позиций обновляются одновременно с ценой
2. **Визуальная обратная связь**: Каждое изменение сопровождается анимацией вспышки (up/down)
3. **Более полное обновление**: Теперь обновляются ВСЕ данные позиций, а не только профит
4. **Консистентность данных**: Все значения обновляются в один момент времени из одного источника

## Тестирование

После применения обновления рекомендуется протестировать:

1. Убедиться, что цена обновляется при получении WebSocket сообщений
2. Проверить, что все числа позиций обновляются одновременно
3. Убедиться, что анимация вспышки работает для всех элементов
4. Проверить, что на других вкладках данные загружаются корректно при переключении

## Файлы, измененные

- `webapp/static/index.html` - расширена функция `updateMarketData()`
