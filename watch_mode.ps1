# Watch Mode - Автоматическая перезагрузка при любых изменениях
# Использование: .\watch_mode.ps1

Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔄 WATCH MODE - Автоматическая перезагрузка при изменениях" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 ОПИСАНИЕ:" -ForegroundColor Yellow
Write-Host "  Этот режим запускает проект один раз и перезагружает его"
Write-Host "  при ЛЮБОМ изменении файлов в проекте"
Write-Host ""

Write-Host "✅ Будет перезагружено при изменении:" -ForegroundColor Green
Write-Host "  ✅ core/ - Логика бота"
Write-Host "  ✅ strategies/ - Стратегии торговли"
Write-Host "  ✅ webapp/ - API endpoints"
Write-Host "  ✅ config/ - Конфигурация"
Write-Host "  ✅ telegram/ - Telegram интеграция"
Write-Host "  ✅ utils/ - Утилиты"
Write-Host "  ✅ Все файлы проекта"
Write-Host ""

Write-Host "❌ НЕ будет перезагружено:" -ForegroundColor Yellow
Write-Host "  ❌ requirements.txt - переустановить зависимости вручную"
Write-Host "  ❌ .env - переменные окружения загружаются при старте"
Write-Host "  ❌ position_state.json - файл состояния позиций"
Write-Host "  ❌ logs/ - логи приложения"
Write-Host "  ❌ __pycache__/ - кэш Python"
Write-Host ""

Write-Host "💡 КАК ИСПОЛЬЗОВАТЬ:" -ForegroundColor Cyan
Write-Host "  1. Запусти скрипт: .\watch_mode.ps1"
Write-Host "  2. Отредактируй любой файл проекта"
Write-Host "  3. Сохрани файл (Ctrl+S)"
Write-Host "  4. Подожди 1-2 сек → Проект перезагружается автоматически"
Write-Host ""

Write-Host "🛑 ОСТАНОВКА:" -ForegroundColor Red
Write-Host "  Нажми Ctrl+C в этом окне"
Write-Host ""

Write-Host "⚙️  ЗАПУСК:" -ForegroundColor Green

# Переменные для мониторинга файлов
$watchPath = Get-Location
$watchFilter = '*.*'
$lastChangeTime = 0
$debounceInterval = 2  # Интервал перезагрузки в секундах
$watcherProcess = $null

# Функция для проверки изменений в файлах
function CheckForChanges {
    # Исключаем папки и файлы которые не должны влиять на перезагрузку
    $excludePaths = @('__pycache__', '.git', 'node_modules', '.pytest_cache', 'logs', '\.pyc$', 'position_state\.json$', '\.log$')
    
    $latestChange = Get-ChildItem -Path $watchPath -Recurse -Exclude @('__pycache__', '.git', 'node_modules', '.pytest_cache', 'logs', '*.pyc', '.pytest_cache') | 
                    Where-Object { 
                        -not $_.PSIsContainer -and
                        -not ($_.FullName -match '\\__pycache__\\') -and
                        -not ($_.FullName -match '\\.git\\') -and
                        -not ($_.FullName -match '\\logs\\') -and
                        -not ($_.FullName -match '\\position_state\.json$') -and
                        -not ($_.FullName -match '\\\.\w+\.swp$')
                    } | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1 -ExpandProperty LastWriteTime
    
    if ($latestChange) {
        $latestChangeUnix = [int64]($latestChange.ToUniversalTime() - (Get-Date -Date "1970-01-01")).TotalSeconds
        if ($latestChangeUnix -gt $script:lastChangeTime) {
            $script:lastChangeTime = $latestChangeUnix
            return $true
        }
    }
    return $false
}

# Функция для перезагрузки и запуска
function RestartBot {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "🔄 Обнаружены изменения! Перезагрузка..." -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host ""
    
    # Завершаем предыдущий процесс если запущен
    if ($script:watcherProcess -ne $null -and -not $script:watcherProcess.HasExited) {
        Write-Host "🛑 Остановка текущего процесса..." -ForegroundColor Cyan
        Stop-Process -InputObject $script:watcherProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
    
    # Запускаем main_dev.py
    Write-Host "▶️  Запуск main_dev.py..." -ForegroundColor Green
    $script:watcherProcess = Start-Process -FilePath "python" -ArgumentList "main_dev.py" -NoNewWindow -PassThru
}

# Инициализация
$script:lastChangeTime = [int64]((Get-Date).ToUniversalTime() - (Get-Date -Date "1970-01-01")).TotalSeconds
$lastCheckTime = Get-Date

# Первый запуск
RestartBot

# Главный цикл мониторинга
Write-Host ""
Write-Host "👁️  Ожидание изменений в файлах... (Ctrl+C для выхода)" -ForegroundColor Cyan
Write-Host ""

try {
    while ($true) {
        # Проверяем изменения каждые 0.5 сек
        if ((Get-Date) - $lastCheckTime -gt (New-TimeSpan -Seconds 0.5)) {
            if (CheckForChanges) {
                Start-Sleep -Seconds $debounceInterval
                RestartBot
            }
            $lastCheckTime = Get-Date
        }
        Start-Sleep -Milliseconds 100
    }
}
finally {
    # Очистка при выходе
    if ($script:watcherProcess -ne $null -and -not $script:watcherProcess.HasExited) {
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host "🛑 Остановка..." -ForegroundColor Red
        Stop-Process -InputObject $script:watcherProcess -Force -ErrorAction SilentlyContinue
        Write-Host "✅ Watch mode завершен" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    }
}
