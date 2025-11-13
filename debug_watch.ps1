# Debug Watch Mode - Отследить какой файл триггерит перезагрузку

$watchPath = Get-Location
$lastChangeTime = [int64]((Get-Date).ToUniversalTime() - (Get-Date -Date "1970-01-01")).TotalSeconds

# Папки и расширения которые НЕ должны триггерить перезагрузку
$ignoredDirs = @('__pycache__', '.git', 'node_modules', '.pytest_cache', 'logs', '.venv', 'venv')
$ignoredExtensions = @('.pyc', '.pyo', '.pyd', '.so', '.swp', '.swo')
$ignoredFiles = @('position_state.json', 'bot_settings.json', 'ml_model.pkl', 'scaler.pkl')

Write-Host "🔍 DEBUG: Отслеживание изменений файлов..." -ForegroundColor Cyan
Write-Host "📁 Путь: $watchPath" -ForegroundColor Cyan
Write-Host ""

$lastCheckedFiles = @{}

try {
    while ($true) {
        $allFiles = Get-ChildItem -Path $watchPath -Recurse -File
        
        foreach ($file in $allFiles) {
            $fullName = $file.FullName
            $fileName = $file.Name
            $extension = $file.Extension
            $lastWriteTime = $file.LastWriteTime
            
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
            
            # Пропускаем если файл игнорируется
            if ($isInIgnoredDir -or $isIgnoredExt -or $isIgnoredFile) {
                continue
            }
            
            $fileKey = $fullName
            
            # Проверяем изменился ли файл
            if ($lastCheckedFiles.ContainsKey($fileKey)) {
                if ($lastCheckedFiles[$fileKey] -ne $lastWriteTime.Ticks) {
                    Write-Host "⚠️  ИЗМЕНЕНИЕ: $fileName" -ForegroundColor Yellow
                    Write-Host "   📍 Путь: $fullName" -ForegroundColor Gray
                    Write-Host "   🕐 Время: $lastWriteTime" -ForegroundColor Gray
                    Write-Host ""
                    $lastCheckedFiles[$fileKey] = $lastWriteTime.Ticks
                }
            } else {
                $lastCheckedFiles[$fileKey] = $lastWriteTime.Ticks
            }
        }
        
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
}
