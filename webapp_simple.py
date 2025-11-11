"""
Упрощенный Web App сервер без зависимостей от торгового бота
Использует только FastAPI и стандартные библиотеки Python
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Настройка кодировки
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

# Создаем приложение FastAPI
app = FastAPI(
    title="KuCoin Trading Bot Web App",
    description="Telegram Web App for trading bot management",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Определяем пути
WEBAPP_DIR = Path(__file__).parent
STATIC_DIR = WEBAPP_DIR / "static"

print(f"[INFO] Webapp directory: {WEBAPP_DIR}", flush=True)
print(f"[INFO] Static directory: {STATIC_DIR}", flush=True)

# Монтируем статические файлы
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print(f"[OK] Static files mounted from {STATIC_DIR}", flush=True)
else:
    print(f"[WARNING] Static directory not found: {STATIC_DIR}", flush=True)

# ============= API ENDPOINTS =============

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {"ping": "pong", "status": "ok"}

@app.get("/")
async def root():
    """Main page - returns index.html"""
    index_path = STATIC_DIR / "index.html"
    
    if index_path.exists():
        print(f"[OK] Serving index.html from {index_path}", flush=True)
        return FileResponse(str(index_path))
    else:
        print(f"[ERROR] index.html not found at {index_path}", flush=True)
        # Возвращаем простую HTML страницу
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Bot</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        .status {
            padding: 15px;
            background: #4CAF50;
            color: white;
            border-radius: 8px;
            margin: 20px 0;
        }
        .info {
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Trading Bot</h1>
        <div class="status">
            ✅ Web App is running!
        </div>
        <div class="info">
            <p><strong>Status:</strong> Server is operational</p>
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Platform:</strong> Amvera Cloud</p>
        </div>
    </div>
</body>
</html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check with detailed info"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "platform": "Amvera Cloud"
    }

@app.get("/api/status")
async def get_status():
    """Get bot status"""
    return {
        "status": "ready",
        "message": "Web App is running. Trading bot can be started via interface.",
        "timestamp": datetime.now().isoformat()
    }

def main():
    """Start the web app"""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    port = int(os.getenv('PORT', 8000))
    
    print("=" * 60, flush=True)
    print("[WEBAPP SIMPLE] Starting simplified Web App", flush=True)
    print("=" * 60, flush=True)
    print(f"[START] Starting on port {port}", flush=True)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
