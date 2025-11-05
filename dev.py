"""
СКРИПТ АВТОМАТИЧЕСКОГО ПЕРЕЗАПУСКА БОТА ПРИ ИЗМЕНЕНИИ ФАЙЛОВ
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotRestartHandler(FileSystemEventHandler):
    """Обработчик изменений файлов"""
    
    def __init__(self, restart_callback):
        super().__init__()
        self.restart_callback = restart_callback
        self.last_event_time = 0
        self.debounce_seconds = 2  # Задержка для группировки множественных изменений
    
    def should_restart(self, file_path):
        """Проверяет, нужно ли перезапускать бота при изменении файла"""
        # Игнорируем изменения в служебных папках и файлах
        ignore_dirs = {'.git', '__pycache__', 'logs', '.vscode', '.idea'}
        ignore_files = {'.env', '.env.example', '*.log', '*.pkl', '*.json'}
        
        file_str = str(file_path)
        
        # Проверяем папки
        for ignore_dir in ignore_dirs:
            if ignore_dir in file_str:
                return False
        
        # Проверяем расширения файлов
        if file_str.endswith('.py'):
            return True
        
        return False
    
    def on_modified(self, event):
        """Обработчик изменения файла"""
        if event.is_directory:
            return
        
        if not self.should_restart(event.src_path):
            return
        
        # Дебаунс - игнорируем множественные события за короткое время
        current_time = time.time()
        if current_time - self.last_event_time < self.debounce_seconds:
            return
        
        self.last_event_time = current_time
        print(f"\n🔄 Обнаружено изменение в файле: {event.src_path}")
        print("⏳ Перезапускаю бота через 2 секунды...")
        
        # Вызываем callback для перезапуска
        self.restart_callback()


class AutoReloadBot:
    """Класс для автоматической перезагрузки бота"""
    
    def __init__(self):
        self.process = None
        self.observer = None
        self.restart_requested = False
        self.script_path = Path(__file__).parent / "main.py"
        
    def start_bot(self):
        """Запускает бота"""
        if self.process:
            print("⚠️  Бот уже запущен")
            return
        
        print("🚀 Запускаю бота...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                stdout=sys.stdout,
                stderr=sys.stderr,
                cwd=str(self.script_path.parent)
            )
            print(f"✅ Бот запущен (PID: {self.process.pid})")
        except Exception as e:
            print(f"❌ Ошибка при запуске бота: {e}")
            self.process = None
    
    def stop_bot(self):
        """Останавливает бота"""
        if not self.process:
            return
        
        print("🛑 Останавливаю бота...")
        try:
            # Пытаемся корректно завершить процесс
            if sys.platform == "win32":
                self.process.terminate()
            else:
                self.process.send_signal(signal.SIGTERM)
            
            # Ждем завершения процесса (максимум 5 секунд)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Принудительно убиваем процесс
                print("⚠️  Принудительное завершение процесса...")
                self.process.kill()
                self.process.wait()
            
            print("✅ Бот остановлен")
        except Exception as e:
            print(f"❌ Ошибка при остановке бота: {e}")
        finally:
            self.process = None
    
    def restart_bot(self):
        """Перезапускает бота"""
        self.restart_requested = True
        self.stop_bot()
        time.sleep(1)  # Небольшая задержка перед перезапуском
        self.start_bot()
        self.restart_requested = False
    
    def start_watcher(self):
        """Запускает наблюдатель за файлами"""
        event_handler = BotRestartHandler(self.restart_bot)
        self.observer = Observer()
        
        # Отслеживаем все .py файлы в корне проекта
        project_root = Path(__file__).parent
        self.observer.schedule(event_handler, str(project_root), recursive=True)
        
        print("👀 Отслеживание изменений файлов запущено...")
        print(f"📁 Наблюдаю папку: {project_root}")
        self.observer.start()
    
    def run(self):
        """Основной цикл работы"""
        print("=" * 60)
        print("🔥 АВТОМАТИЧЕСКИЙ РЕЖИМ РАЗРАБОТКИ")
        print("=" * 60)
        print("📝 Бот будет автоматически перезапускаться при изменении .py файлов")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("=" * 60)
        print()
        
        # Запускаем бота
        self.start_bot()
        
        # Запускаем наблюдатель
        self.start_watcher()
        
        try:
            # Мониторим процесс бота
            while True:
                if self.process:
                    # Проверяем, завершился ли процесс
                    if self.process.poll() is not None:
                        if not self.restart_requested:
                            print("\n⚠️  Бот завершился неожиданно")
                            print("🔄 Перезапускаю через 3 секунды...")
                            time.sleep(3)
                            self.start_bot()
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Получен сигнал остановки...")
            self.stop_bot()
            if self.observer:
                self.observer.stop()
                self.observer.join()
            print("👋 До свидания!")


if __name__ == "__main__":
    reloader = AutoReloadBot()
    reloader.run()
