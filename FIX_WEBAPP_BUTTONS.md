# Исправление ошибки WebAppPopupParamInvalid

## Проблема
При нажатии на кнопки "Запустить" и "Остановить" в Telegram Web App возникала ошибка:
```
Ошибка: WebAppPopupParamInvalid
```

## Причина
Использовался неправильный метод `tg.showAlert()`, который принимает только один строковый параметр. При передаче дополнительных параметров или использовании в определенных контекстах может возникать ошибка `WebAppPopupParamInvalid`.

## Решение
Заменили `tg.showAlert(message)` на `tg.showPopup(params)` с правильной структурой параметров.

### Было (неправильно):
```javascript
tg.showAlert(result.message);
```

### Стало (правильно):
```javascript
tg.showPopup({
  title: 'Бот',
  message: result.message || 'Готово',
  buttons: [{ type: 'ok' }]
});
```

## Изменения в коде

### Файл: `webapp/static/index.html`

#### Функция startBot():
```javascript
async function startBot() {
  try {
    const response = await fetch(`${API_URL}/bot/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ init_data: initData })
    });

    const result = await response.json();
    
    // Используем showPopup вместо showAlert для корректной работы
    tg.showPopup({
      title: 'Бот',
      message: result.message || 'Готово',
      buttons: [{ type: 'ok' }]
    });
    
    loadData();
  } catch (error) {
    tg.showPopup({
      title: 'Ошибка',
      message: error.message || 'Произошла ошибка',
      buttons: [{ type: 'ok' }]
    });
  }
}
```

#### Функция stopBot():
```javascript
async function stopBot() {
  try {
    const response = await fetch(`${API_URL}/bot/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ init_data: initData })
    });

    const result = await response.json();
    
    // Используем showPopup вместо showAlert для корректной работы
    tg.showPopup({
      title: 'Бот',
      message: result.message || 'Готово',
      buttons: [{ type: 'ok' }]
    });
    
    loadData();
  } catch (error) {
    tg.showPopup({
      title: 'Ошибка',
      message: error.message || 'Произошла ошибка',
      buttons: [{ type: 'ok' }]
    });
  }
}
```

## Документация Telegram Web App API

### showPopup()
Показывает всплывающее окно с кнопками.

**Параметры:**
```javascript
{
  title: string,        // Заголовок (необязательно, максимум 64 символа)
  message: string,      // Текст сообщения (обязательно, 1-256 символов)
  buttons: Array        // Массив кнопок (обязательно, 1-3 кнопки)
}
```

**Типы кнопок:**
- `'ok'` - Кнопка ОК
- `'close'` - Кнопка закрытия
- `'cancel'` - Кнопка отмены
- `'default'` - Пользовательская кнопка
- `'destructive'` - Опасное действие

**Пример:**
```javascript
tg.showPopup({
  title: 'Подтверждение',
  message: 'Вы уверены?',
  buttons: [
    { type: 'ok', text: 'Да' },
    { type: 'cancel' }
  ]
}, function(buttonId) {
  console.log('Нажата кнопка:', buttonId);
});
```

### showAlert()
Простое уведомление без кнопок (используется редко).

**Параметры:**
```javascript
tg.showAlert(message, callback);
```

⚠️ **Внимание:** `showAlert()` может вызывать ошибки в некоторых случаях. Рекомендуется использовать `showPopup()`.

## Тестирование

Для тестирования создан файл `tests/test_buttons_fix.html`, который можно открыть в браузере:
```
http://localhost:8000/static/test_buttons_fix.html
```

Или через тестовый файл:
```bash
start tests/test_buttons_fix.html
```

## Проверка работы

1. Запустите веб-приложение:
   ```bash
   python webapp_only.py
   ```

2. Откройте в Telegram или через браузер:
   - В Telegram: через @BotFather -> Web App URL
   - В браузере: http://localhost:8000

3. Нажмите на кнопки "Запустить" или "Остановить"

4. Должно появиться всплывающее окно с сообщением (без ошибок)

## Результат
✅ Ошибка `WebAppPopupParamInvalid` исправлена  
✅ Кнопки работают корректно  
✅ Уведомления отображаются правильно  

## Дополнительные улучшения

Можно добавить более сложные диалоги с несколькими кнопками:

```javascript
tg.showPopup({
  title: 'Запуск бота',
  message: 'Начать торговлю?',
  buttons: [
    { id: 'start', type: 'default', text: 'Запустить' },
    { id: 'cancel', type: 'cancel' }
  ]
}, function(buttonId) {
  if (buttonId === 'start') {
    // Запускаем бота
  }
});
```

## Ссылки
- [Telegram Web Apps API](https://core.telegram.org/bots/webapps)
- [Документация showPopup](https://core.telegram.org/bots/webapps#popupparams)
