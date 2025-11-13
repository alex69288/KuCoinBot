import os

def pytest_ignore_collect(path=None, config=None, collection_path=None):
    """Игнорируем файл с точками в имени для совместимости с pytest>=8.

    PyTest 8 де-прикрепил py.path.local для аргумента path и предлагает
    использовать collection_path (pathlib.Path). Поддержим оба варианта.
    """
    p = collection_path or path
    try:
        basename = os.path.basename(str(p))
    except Exception:
        basename = str(p)
    return basename == 'test_websocket_fix_v0.1.8.py'
