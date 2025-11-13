"""
Конфигурация asyncio для корректной работы на Windows и других платформах
Избегает проблем с ProactorEventLoop и ConnectionResetError
"""
import sys
import asyncio
from utils.logger import log_info, log_error


def configure_asyncio():
    """
    Конфигурирует asyncio event loop для корректной работы на всех платформах.
    
    На Windows:
    - Использует SelectorEventLoop вместо ProactorEventLoop (избегает проблем с закрытием соединений)
    - Отключает обработку SIGINT/SIGTERM (для Windows)
    
    На других платформах:
    - Использует стандартный event loop
    
    Проблема: ProactorEventLoop на Windows может выбросить ConnectionResetError
    в обработчике _ProactorBasePipeTransport._call_connection_lost() при закрытии
    WebSocket соединений.
    """
    try:
        if sys.platform == 'win32':
            # На Windows используем SelectorEventLoop вместо ProactorEventLoop
            # ProactorEventLoop имеет проблемы с WebSocket и может выбросить ConnectionResetError
            # See: https://github.com/encode/starlette/issues/1529
            
            log_info("[ASYNCIO] Windows обнаружена - настраиваем event loop")
            
            # Проверяем текущий policy
            current_policy = asyncio.get_event_loop_policy()
            log_info(f"[ASYNCIO] Текущий event loop policy: {current_policy}")
            
            # Устанавливаем WindowsSelectorEventLoopPolicy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            # Получаем новый loop
            if sys.version_info >= (3, 10):
                loop = asyncio.new_event_loop()
            else:
                loop = asyncio.new_event_loop()
            
            asyncio.set_event_loop(loop)
            
            log_info("[ASYNCIO] ✅ Установлен WindowsSelectorEventLoopPolicy")
            log_info("[ASYNCIO] Это решает проблему с ConnectionResetError в ProactorEventLoop")
            
        else:
            # На Unix/Linux используем стандартный event loop
            log_info("[ASYNCIO] Unix/Linux обнаружена - используем стандартный event loop")
            
    except Exception as e:
        log_error(f"[ASYNCIO] Ошибка при конфигурации event loop: {e}")
        raise


def suppress_asyncio_debug_warnings():
    """
    Подавляет предупреждения asyncio при отладке
    """
    try:
        if sys.platform == 'win32':
            # На Windows отключаем отладку asyncio для уменьшения шума в логах
            try:
                loop = asyncio.get_event_loop()
                loop.set_debug(False)
            except RuntimeError:
                # Если loop еще не создан, ничего не делаем
                pass
    except Exception as e:
        log_error(f"[ASYNCIO] Ошибка при отключении debug: {e}")


__all__ = ['configure_asyncio', 'suppress_asyncio_debug_warnings']
