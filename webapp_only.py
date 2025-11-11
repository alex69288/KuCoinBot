"""
Упрощенный запуск только Web App для Amvera
Без обязательной проверки переменных окружения - они нужны будут только при запуске бота
"""
import sys
import os
import time

# Отключаем буферизацию вывода
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Добавляем путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Запуск только Web App без торгового бота"""
    # Настройка вывода для работы с любой кодировкой
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    start_time = time.time()
    
    print("=" * 60, flush=True)
    print("[WEB APP] Starting Web App (interface only)", flush=True)
    print("=" * 60, flush=True)
    
    try:
        # Импортируем необходимые модули
        print("[IMPORT] Loading modules...", flush=True)
        
        print("  - Importing uvicorn...", flush=True)
        import uvicorn
        print("  [OK] uvicorn", flush=True)
        
        print("  - Importing webapp.server...", flush=True)
        from webapp.server import app
        print("  [OK] webapp.server", flush=True)
        
        # Получаем порт из переменной окружения
        port = int(os.getenv('PORT', 8000))
        
        print("\n" + "=" * 60, flush=True)
        print(f"[OK] Initialization completed in {time.time() - start_time:.2f} sec", flush=True)
        print(f"[START] Starting WEB APP on port {port}", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
        print("[INFO] Trading bot will be started via web interface", flush=True)
        print("       after setting environment variables in Amvera.", flush=True)
        print("", flush=True)
        print("[ENV] Required environment variables:", flush=True)
        print("   - KUCOIN_API_KEY", flush=True)
        print("   - KUCOIN_SECRET_KEY", flush=True)
        print("   - KUCOIN_PASSPHRASE", flush=True)
        print("   - TELEGRAM_BOT_TOKEN", flush=True)
        print("   - TELEGRAM_CHAT_ID", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
        
        # Запускаем Uvicorn как ГЛАВНЫЙ процесс
        print("[UVICORN] Starting Uvicorn server...", flush=True)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=30,
        )
        
    except ImportError as e:
        print(f"\n[ERROR] Import error: {e}", flush=True)
        print("Check that all dependencies are installed:", flush=True)
        print("  pip install -r requirements.txt", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n[STOP] Received shutdown signal", flush=True)
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
