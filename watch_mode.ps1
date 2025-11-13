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
Write-Host "  ❌ bot_settings.json - настройки бота"
Write-Host "  ❌ ml_model.pkl - ML модель"
Write-Host "  ❌ scaler.pkl - скейлер признаков"
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
    # Папки и расширения которые НЕ должны триггерить перезагрузку
    $ignoredDirs = @('__pycache__', '.git', 'node_modules', '.pytest_cache', 'logs', '.venv', 'venv')
    $ignoredExtensions = @('.pyc', '.pyo', '.pyd', '.so', '.swp', '.swo')
    $ignoredFiles = @('position_state.json', 'bot_settings.json', 'ml_model.pkl', 'scaler.pkl')
    
    $latestChange = Get-ChildItem -Path $watchPath -Recurse -File | 
                    Where-Object { 
                        $file = $_
                        $fullName = $_.FullName
                        $fileName = $_.Name
                        $extension = $_.Extension
                        
                        # Проверяем что файл не в исключенных папках
                        $isInIgnoredDir = $false
                        foreach ($ignoredDir in $ignoredDirs) {
                            if ($fullName -like "*\$ignoredDir\*") {
                                $isInIgnoredDir = $true
                                break
                            }
                        }
                        
                        # Проверяем расширение
                        $isIgnoredExt = $extension -in $ignoredExtensions
                        
                        # Проверяем имя файла
                        $isIgnoredFile = $fileName -in $ignoredFiles
                        
                        # Возвращаем true если файл НЕ игнорируется
                        -not $isInIgnoredDir -and -not $isIgnoredExt -and -not $isIgnoredFile
                    } | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1
    
    if ($latestChange) {
        $latestChangeUnix = [int64]($latestChange.LastWriteTime.ToUniversalTime() - (Get-Date -Date "1970-01-01")).TotalSeconds
        if ($latestChangeUnix -gt $script:lastChangeTime) {
            Write-Host "  📝 Изменение: $($latestChange.Name)" -ForegroundColor Gray
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
