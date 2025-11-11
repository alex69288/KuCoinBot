# Скрипт быстрого запуска бота для локальной разработки
# Автор: KuCoin Trading Bot
# Использование: .\start_local.ps1

# Цвета для вывода
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error-Custom { Write-Host $args -ForegroundColor Red }

Clear-Host
Write-Info "═══════════════════════════════════════════════════════════"
Write-Success "  🤖 KuCoin Trading Bot - Локальный запуск"
Write-Info "═══════════════════════════════════════════════════════════"
Write-Host ""

# Проверка наличия Python
Write-Info "🔍 Проверка Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "✅ $pythonVersion"
} catch {
    Write-Error-Custom "❌ Python не найден! Установите Python 3.9 или выше."
    exit 1
}

# Проверка наличия .env файла
Write-Info "🔍 Проверка файла .env..."
if (-not (Test-Path ".env")) {
    Write-Warning "⚠️  Файл .env не найден!"
    Write-Info "📝 Создание .env из .env.example..."
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success "✅ Файл .env создан!"
        Write-Warning "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваши API ключи!"
        Write-Info "📝 Откройте .env в текстовом редакторе и заполните:"
        Write-Host "   - KUCOIN_API_KEY" -ForegroundColor Yellow
        Write-Host "   - KUCOIN_SECRET_KEY" -ForegroundColor Yellow
        Write-Host "   - KUCOIN_PASSPHRASE" -ForegroundColor Yellow
        Write-Host "   - TELEGRAM_BOT_TOKEN" -ForegroundColor Yellow
        Write-Host "   - TELEGRAM_CHAT_ID" -ForegroundColor Yellow
        Write-Host ""
        Write-Info "Нажмите Enter после заполнения .env файла..."
        Read-Host
    } else {
        Write-Error-Custom "❌ Файл .env.example не найден!"
        exit 1
    }
} else {
    Write-Success "✅ Файл .env найден"
}

# Проверка зависимостей
Write-Info "🔍 Проверка зависимостей..."
$needInstall = $false

try {
    python -c "import ccxt, telegram, fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $needInstall = $true
    }
} catch {
    $needInstall = $true
}

if ($needInstall) {
    Write-Warning "⚠️  Некоторые зависимости отсутствуют"
    Write-Info "📦 Установка зависимостей из requirements.txt..."
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "❌ Ошибка установки зависимостей!"
        exit 1
    }
    Write-Success "✅ Зависимости установлены"
} else {
    Write-Success "✅ Все зависимости установлены"
}

# Проверка переменных окружения
Write-Info "🔍 Проверка переменных окружения..."
python tests/check_env.py 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Warning "⚠️  Некоторые переменные окружения не настроены"
    Write-Info "📝 Проверьте файл .env и убедитесь, что все ключи заполнены"
    $continue = Read-Host "Продолжить запуск? (y/n)"
    if ($continue -ne "y") {
        Write-Info "Запуск отменен"
        exit 0
    }
}

Write-Host ""
Write-Info "═══════════════════════════════════════════════════════════"
Write-Success "  🚀 Запуск бота..."
Write-Info "═══════════════════════════════════════════════════════════"
Write-Host ""
Write-Info "📊 Web интерфейс будет доступен на: http://localhost:8000"
Write-Info "🤖 Telegram бот будет активен"
Write-Info "📝 Логи сохраняются в папку: logs/"
Write-Host ""
Write-Warning "Для остановки нажмите Ctrl+C"
Write-Host ""

# Запуск бота
python main_with_webapp.py
