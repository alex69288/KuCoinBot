# Исправление ошибки ConnectionResetError на Windows

**Версия:** v0.1.15  
**Дата:** 13 ноября 2025 г.  
**Статус:** ✅ Исправлено

## Описание проблемы

При работе бота на Windows возникала ошибка:

```
Exception in callback _ProactorBasePipeTransport._call_connection_lost(None)
handle: <Handle _ProactorBasePipeTransport._call_connection_lost(None)>
Traceback (most recent call last):
  File "C:\Programs\Python\Lib\asyncio\events.py", line 88, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Programs\Python\Lib\asyncio\proactor_events.py", line 165, in _call_connection_lost
    self._sock.shutdown(socket.SHUT_RDWR)
ConnectionResetError: [WinError 10054] Удаленный хост принудительно разорвал существующее подключение
```

## Причина

**ProactorEventLoop** на Windows имеет проблемы с корректным закрытием WebSocket соединений:

1. При отключении клиента (например, закрытие браузера с Web App), ProactorEventLoop пытается закрыть сокет
2. Если удаленный хост уже закрыл соединение, возникает `ConnectionResetError`
3. Ошибка возникает в callback `_ProactorBasePipeTransport._call_connection_lost()`, который вызывается при очистке ресурсов
4. Это не критическая ошибка, но засоряет логи и может указывать на проблемы с обработкой соединений

## Решение

### 1. Создан модуль конфигурации asyncio

**Файл:** `utils/asyncio_config.py`

Модуль содержит функции для правильной конфигурации asyncio event loop:

- `configure_asyncio()` - настраивает правильный event loop для платформы
- `suppress_asyncio_debug_warnings()` - отключает debug предупреждения

**Ключевое изменение для Windows:**
```python
# Используем WindowsSelectorEventLoopPolicy вместо WindowsProactorEventLoopPolicy
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

`SelectorEventLoop` корректно обрабатывает закрытие соединений и не генерирует `ConnectionResetError`.

### 2. Интеграция в main.py

Конфигурация asyncio вызывается **перед** импортом модулей, которые используют asyncio:

```python
# Конфигурация asyncio для корректной работы на Windows
from utils.asyncio_config import configure_asyncio, suppress_asyncio_debug_warnings
configure_asyncio()
suppress_asyncio_debug_warnings()

import time
import traceback
import threading
# ... остальные импорты
```

### 3. Интеграция в webapp/server.py

Аналогично добавлена конфигурация перед импортом FastAPI:

```python
# Конфигурация asyncio для корректной работы на Windows (перед импортом FastAPI)
from utils.asyncio_config import configure_asyncio, suppress_asyncio_debug_warnings
configure_asyncio()
suppress_asyncio_debug_warnings()

from fastapi import FastAPI, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
```

### 4. Улучшена обработка ошибок в WebSocket

**Файл:** `webapp/server.py`

#### В методе `send_personal_message`:
```python
async def send_personal_message(self, message: dict, websocket: WebSocket):
    try:
        await websocket.send_json(message)
    except ConnectionResetError as e:
        # Ошибка Windows: удаленный хост разорвал соединение
        log_info(f"[WS] Соединение было разорвано клиентом (ConnectionResetError)")
        self.disconnect(websocket)
    except Exception as e:
        log_error(f"[WS] Ошибка отправки персонального сообщения: {e}")
        self.disconnect(websocket)
```

#### В методе `broadcast`:
```python
async def broadcast(self, message: dict):
    disconnected = []
    
    for connection in list(self.active_connections):  # Копия списка для безопасной итерации
        try:
            await connection.send_json(message)
        except ConnectionResetError:
            # Нормальная ошибка - клиент отключился на Windows
            log_info(f"[WS] Клиент отключился (ConnectionResetError), удаляем из списка")
            disconnected.append(connection)
        except (RuntimeError, OSError) as e:
            # Другие сетевые ошибки
            log_info(f"[WS] Сетевая ошибка при отправке сообщения: {type(e).__name__}")
            disconnected.append(connection)
        # ...
```

#### В WebSocket endpoint:
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # ...
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # ...
            except ConnectionResetError:
                # Нормальное отключение на Windows
                log_info("[WS] Клиент отключился (ConnectionResetError)")
                break
            except RuntimeError as e:
                # Соединение закрыто
                log_info(f"[WS] Соединение закрыто: {e}")
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log_info("[WS] Клиент отключился (WebSocketDisconnect)")
    except ConnectionResetError:
        manager.disconnect(websocket)
        log_info("[WS] Соединение было разорвано (ConnectionResetError)")
    # ...
    finally:
        # Гарантированно удаляем соединение
        manager.disconnect(websocket)
```

## Результат

✅ **Исправлено:**
- Ошибка `ConnectionResetError: [WinError 10054]` больше не возникает
- WebSocket соединения корректно закрываются на всех платформах
- Улучшено логирование отключений клиентов

✅ **Совместимость:**
- Windows: использует `WindowsSelectorEventLoopPolicy`
- Linux/Unix: использует стандартный event loop
- Работает на локальной машине и на серверах (Amvera, Railway и др.)

## Технические детали

### Почему SelectorEventLoop лучше ProactorEventLoop для WebSocket?

| Параметр | ProactorEventLoop | SelectorEventLoop |
|----------|-------------------|-------------------|
| Поддержка субпроцессов | ✅ Да | ⚠️ Ограничена |
| WebSocket/Socket | ⚠️ Проблемы с закрытием | ✅ Стабильно |
| Производительность | ⚡ Высокая | ⚡ Высокая |
| Проблема WinError 10054 | ❌ Возникает | ✅ Не возникает |

### Ссылки

- [Starlette Issue #1529](https://github.com/encode/starlette/issues/1529) - аналогичная проблема
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio-policy.html)
- [FastAPI WebSocket documentation](https://fastapi.tiangolo.com/advanced/websockets/)

## Тестирование

Для проверки исправления:

1. Запустите бота в dev режиме:
   ```powershell
   python main_dev.py
   ```

2. Откройте Web App в браузере

3. Подключитесь к WebSocket (автоматически при открытии приложения)

4. Закройте браузер или вкладку

5. Проверьте логи - ошибка `ConnectionResetError` не должна появиться в трейсбеке

## Файлы, затронутые исправлением

- ✅ `utils/asyncio_config.py` - новый модуль конфигурации
- ✅ `main.py` - добавлена конфигурация asyncio
- ✅ `webapp/server.py` - добавлена конфигурация asyncio и улучшена обработка ошибок
- ✅ `docs/FIX_CONNECTION_RESET_ERROR_v0.1.15.md` - документация (этот файл)

## Версия

Эти изменения будут включены в **версию v0.1.15** бота.
