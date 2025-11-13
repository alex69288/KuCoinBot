#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEV MODE - Запуск бота с горячей перезагрузкой (Hot Reload)
Для локальной разработки - автоматически перезагружает сервер при изменении файлов
"""
import sys
import os

# 🔧 Исправление кодировки консоли для Windows (UTF-8)
if sys.platform == 'win32':
    import io
    import codecs
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
import time
from dotenv import load_dotenv

print("=" * 70, flush=True)
print("🔄 DEV MODE - Запуск с горячей перезагрузкой (Hot Reload)", flush=True)
print("=" * 70, flush=True)
print("\n📋 Что будет перезагружено при изменении файлов:", flush=True)
print("   ✅ webapp/server.py - Endpoints API", flush=True)
print("   ✅ webapp/api_compact_responses.py - Компактные ответы API", flush=True)
print("   ✅ Все файлы в папке webapp/", flush=True)
print("\n⚠️  Что НЕ перезагружается (нужен ручной перезапуск):", flush=True)
print("   - core/bot.py - Основной бот", flush=True)
print("   - strategies/ - Стратегии торговли", flush=True)
print("   - config/ - Конфигурация", flush=True)
print("\n💡 Совет: Используйте этот режим только для разработки API!", flush=True)
print("=" * 70, flush=True)

# Загружаем переменные окружения
print("\n📁 Загрузка переменных окружения из .env файла...", flush=True)
load_dotenv()
print("✅ Переменные загружены\n", flush=True)

# Запускаем Uvicorn с hot reload на только webapp файлы
port = int(os.getenv('PORT', 8000))

print(f"🌐 Запуск Uvicorn с горячей перезагрузкой на порту {port}...\n", flush=True)

# Используем uvicorn напрямую с reload
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'webapp.server_dev:app',  # Используем специальный модуль для dev
    '--host', '0.0.0.0',
    '--port', str(port),
    '--reload',  # Горячая перезагрузка
    '--reload-dir', 'webapp',  # Только смотрим за папкой webapp (правильное имя параметра)
    '--log-level', 'info'
], cwd=os.path.dirname(os.path.abspath(__file__)))
