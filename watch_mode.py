#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WATCH MODE - Автоматическая перезагрузка при изменении любых файлов
Это как горячая перезагрузка, но для ВСЕ проекта, включая логику бота
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
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
print("=" * 70, flush=True)
print("🔄 WATCH MODE - Автоматическая перезагрузка при изменениях", flush=True)
print("=" * 70, flush=True)
print("\n📋 Что будет перезагружено при изменении файлов:", flush=True)
print("   ✅ core/ - Логика бота", flush=True)
print("   ✅ strategies/ - Стратегии торговли", flush=True)
print("   ✅ webapp/ - API endpoints", flush=True)
print("   ✅ config/ - Конфигурация", flush=True)
print("   ✅ telegram/ - Telegram интеграция", flush=True)
print("   ✅ utils/ - Утилиты", flush=True)
print("   ✅ ВСЕ файлы проекта", flush=True)
print("\n❌ Что НЕ будет перезагружено:", flush=True)
print("   - requirements.txt - нужна переустановка зависимостей", flush=True)
print("   - .env - переменные окружения (используются при запуске)", flush=True)
print("\n💡 Совет: Сохраняй файл (Ctrl+S) → Проект перезагружается автоматически!", flush=True)
print("🛑 Остановка: Нажми Ctrl+C", flush=True)
print("=" * 70, flush=True)

load_dotenv()
print("\n📁 Загрузка переменных окружения из .env файла...", flush=True)

# Список расширений файлов, за которыми нужно следить
WATCH_EXTENSIONS = {
    '.py', '.json', '.yaml', '.yml', '.txt', '.md', '.html', '.css', '.js'
}

# Список папок/файлов, которые нужно игнорировать
IGNORE_PATTERNS = {
    '__pycache__', '.git', '.vscode', '.pytest_cache', 'node_modules',
    '.pyc', '.pyo', '.egg-info', 'build', 'dist', '.env.local'
}

class ProjectWatcher(FileSystemEventHandler):
    """Следит за изменениями файлов проекта"""
    
    def __init__(self):
        self.process = None
        self.last_change_time = time.time()
        self.debounce_time = 1.0  # Ждём 1 сек перед перезагрузкой
        self.pending_restart = False
        
    def should_watch_file(self, file_path):
        """Проверяет, нужно ли следить за этим файлом"""
        path_str = str(file_path)
        
        # Игнорируем определённые папки/файлы
        for pattern in IGNORE_PATTERNS:
            if pattern in path_str:
                return False
        
        # Проверяем расширение
        return Path(file_path).suffix in WATCH_EXTENSIONS
    
    def on_modified(self, event):
        """Вызывается при изменении файла"""
        if event.is_directory:
            return
        
        if not self.should_watch_file(event.src_path):
            return
        
        print(f"\n📝 Изменён файл: {Path(event.src_path).name}", flush=True)
        self.request_restart()
    
    def on_created(self, event):
        """Вызывается при создании файла"""
        if event.is_directory:
            return
        
        if not self.should_watch_file(event.src_path):
            return
        
        print(f"\n✨ Создан файл: {Path(event.src_path).name}", flush=True)
        self.request_restart()
    
    def on_deleted(self, event):
        """Вызывается при удалении файла"""
        if event.is_directory:
            return
        
        if not self.should_watch_file(event.src_path):
            return
        
        print(f"\n🗑️  Удалён файл: {Path(event.src_path).name}", flush=True)
        self.request_restart()
    
    def request_restart(self):
        """Запрашивает перезагрузку (с debounce)"""
        current_time = time.time()
        
        # Debounce: если последнее изменение было недавно, ждём
        if self.pending_restart:
            return
        
        self.pending_restart = True
        time.sleep(self.debounce_time)
        self.restart_process()
        self.pending_restart = False
    
    def restart_process(self):
        """Перезагружает основной процесс"""
        print("\n🔄 Перезагрузка проекта...", flush=True)
        
        # Останавливаем старый процесс
        if self.process:
            print("  ⏹️  Остановка текущего процесса...", flush=True)
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("  ⚠️  Процесс не остановился, принудительное завершение...", flush=True)
                self.process.kill()
            print("  ✅ Процесс остановлен", flush=True)
        
        # Запускаем новый процесс
        print("  🚀 Запуск нового процесса...", flush=True)
        self.process = subprocess.Popen(
            [sys.executable, 'main_local.py'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("  ✅ Процесс запущен!\n", flush=True)

def main():
    """Основная функция"""
    watcher = ProjectWatcher()
    
    # Запускаем первый раз
    print("\n🚀 Первый запуск проекта...\n", flush=True)
    watcher.restart_process()
    
    # Создаём Observer
    observer = Observer()
    
    # Следим за всеми папками проекта
    watch_dirs = [
        'core', 'strategies', 'webapp', 'config', 'telegram', 'utils', 
        'analytics', 'ml', 'deploy', 'tests'
    ]
    
    for watch_dir in watch_dirs:
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), watch_dir)
        if os.path.exists(dir_path):
            print(f"👁️  Следим за папкой: {watch_dir}/", flush=True)
            observer.schedule(watcher, dir_path, recursive=True)
    
    # Также следим за корневыми .py файлами
    observer.schedule(watcher, os.path.dirname(os.path.abspath(__file__)), recursive=False)
    
    print("\n✅ Watch mode активирован!", flush=True)
    print("💾 Сохраняй файлы → Проект автоматически перезагружается", flush=True)
    print("⏱️  Подожди 1-2 сек после сохранения файла (debounce)\n", flush=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Остановка watch mode...", flush=True)
        observer.stop()
        observer.join()
        
        if watcher.process:
            print("🛑 Остановка процесса приложения...", flush=True)
            watcher.process.terminate()
            try:
                watcher.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                watcher.process.kill()
        
        print("✅ Завершено\n", flush=True)
        sys.exit(0)

if __name__ == '__main__':
    main()
