"""
ТЕСТ ИМПОРТОВ - НАХОДИМ ЗАВИСШИЙ МОДУЛЬ
"""
import sys
import time

def test_import(module_name):
    """Тестирует импорт модуля с таймером"""
    print(f"⏱️  Импортируем {module_name}...", flush=True)
    start_time = time.time()
    try:
        __import__(module_name)
        elapsed = time.time() - start_time
        print(f"✅ {module_name} - импортирован за {elapsed:.2f}сек", flush=True)
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {module_name} - ОШИБКА за {elapsed:.2f}сек: {e}", flush=True)
        return False

if __name__ == "__main__":
    print("=" * 60, flush=True)
    print("🔍 ДИАГНОСТИКА ИМПОРТОВ", flush=True)
    print("=" * 60, flush=True)
    
    # Тестируем базовые модули
    modules_to_test = [
        'dotenv',
        'ccxt',
        'sklearn',
        'numpy',
        'utils.logger',
        'config.constants',
        'config.settings',
        'core.exchange',
        'core.risk_manager',
        'analytics.metrics',
        'ml.features',
        'ml.model',
        'strategies.base_strategy',
        'strategies.ema_ml',
        'strategies.price_action',
        'strategies.macd_rsi',
        'strategies.bollinger',
        'telegram.menus',
        'telegram.handlers',
        'telegram.bot',
        'core.bot',
    ]
    
    for module in modules_to_test:
        test_import(module)
        print("", flush=True)
    
    print("=" * 60, flush=True)
    print("✅ ТЕСТ ЗАВЕРШЕН", flush=True)
    print("=" * 60, flush=True)
