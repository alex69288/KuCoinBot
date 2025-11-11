"""
Тест проверки исправлений Web App - стили и API
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("ТЕСТ: Проверка исправлений Web App")
print("=" * 60)

# 1. Проверка index.html
print("\n1. Проверка структуры index.html...")
html_path = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html')

if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем отсутствие дублированных тегов
    issues = []
    
    if content.count('<!DOCTYPE html>') > 1:
        issues.append("❌ Найдено несколько <!DOCTYPE html>")
    else:
        print("✅ <!DOCTYPE html> - один")
    
    if content.count('<html') > 1:
        issues.append("❌ Найдено несколько <html>")
    else:
        print("✅ <html> - один")
    
    if content.count('<head>') > 1:
        issues.append("❌ Найдено несколько <head>")
    else:
        print("✅ <head> - один")
    
    if content.count('<body>') > 1:
        issues.append("❌ Найдено несколько <body>")
    else:
        print("✅ <body> - один")
    
    # Проверяем наличие основных элементов
    if '<style>' in content:
        print("✅ CSS стили присутствуют")
    else:
        issues.append("❌ CSS стили отсутствуют")
    
    if 'telegram-web-app.js' in content:
        print("✅ Telegram Web App SDK подключен")
    else:
        issues.append("❌ Telegram Web App SDK не подключен")
    
    if issues:
        print("\n⚠️ Найдены проблемы:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Структура HTML корректна")
else:
    print("❌ Файл index.html не найден")

# 2. Проверка server.py
print("\n2. Проверка server.py...")
server_path = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'server.py')

if os.path.exists(server_path):
    with open(server_path, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Проверяем использование правильного метода
    if 'exchange.fetch_ticker' in server_content:
        print("❌ Найдено использование exchange.fetch_ticker (неправильно)")
    else:
        print("✅ Не используется неправильный метод fetch_ticker")
    
    if 'exchange.get_ticker' in server_content:
        print("✅ Используется правильный метод get_ticker")
    else:
        print("❌ Не найдено использование get_ticker")
else:
    print("❌ Файл server.py не найден")

# 3. Проверка наличия резервной копии
print("\n3. Проверка резервной копии...")
backup_path = os.path.join(os.path.dirname(__file__), '..', 'webapp', 'static', 'index.html.backup')

if os.path.exists(backup_path):
    print("✅ Резервная копия создана")
else:
    print("⚠️ Резервная копия не найдена (это нормально, если она была удалена)")

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 60)
