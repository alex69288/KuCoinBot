"""
Минимальный тестовый сервер для проверки работы на Amvera
Если этот сервер не работает, значит проблема в инфраструктуре
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
import uvicorn

# Создаем минимальное приложение
app = FastAPI(title="KuCoin Bot Test Server")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "status": "ok",
        "message": "Минимальный тестовый сервер работает!",
        "server": "Amvera Cloud"
    }

@app.get("/ping")
async def ping():
    """Проверка доступности"""
    return {"ping": "pong"}

@app.get("/health")
async def health():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "python_version": sys.version,
        "cwd": os.getcwd()
    }

def main():
    """Запуск минимального сервера"""
    print("=" * 60, flush=True)
    print("🧪 ТЕСТОВЫЙ СЕРВЕР", flush=True)
    print("=" * 60, flush=True)
    
    port = int(os.getenv('PORT', 8000))
    
    print(f"🚀 Запуск на порту {port}", flush=True)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
