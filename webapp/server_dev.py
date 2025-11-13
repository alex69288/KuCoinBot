"""
DEV SERVER - Упрощённая версия для разработки с горячей перезагрузкой
Загружает бота один раз и использует его для всех запросов
"""
import os
import sys

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Импортируем основной app из server
from webapp.server import app, set_trading_bot

# Создаём глобальный экземпляр бота (инициализируется один раз при импорте)
try:
    from core.bot import AdvancedTradingBot
    print("\n📦 Инициализация бота для dev сервера...", flush=True)
    trading_bot = AdvancedTradingBot()
    set_trading_bot(trading_bot)
    print("✅ Бот инициализирован для dev режима\n", flush=True)
except Exception as e:
    print(f"\n❌ Ошибка инициализации бота: {e}", flush=True)
    trading_bot = None

# Экспортируем app для uvicorn
# Используется как: uvicorn webapp.server_dev:app --reload
