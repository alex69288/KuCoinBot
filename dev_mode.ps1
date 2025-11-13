# Dev Mode - Запуск с горячей перезагрузкой
# Использование: .\dev_mode.ps1

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host " DEV MODE - Горячая перезагрузка (Hot Reload) " -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 ОПИСАНИЕ:" -ForegroundColor Yellow
Write-Host "  Этот режим автоматически перезагружает API при изменении файлов в webapp/"
Write-Host ""
Write-Host "🔄 Будет перезагружено при изменении:" -ForegroundColor Green
Write-Host "  ✅ webapp/server.py"
Write-Host "  ✅ webapp/api_compact_responses.py"
Write-Host "  ✅ Все файлы в webapp/"
Write-Host ""
Write-Host "⚠️  НЕ будет перезагружено (нужна перезагрузка вручную):" -ForegroundColor Yellow
Write-Host "  ❌ core/bot.py"
Write-Host "  ❌ strategies/"
Write-Host "  ❌ config/"
Write-Host "  ❌ utils/"
Write-Host ""
Write-Host "💡 ГОРЯЧИЕ КЛАВИШИ:" -ForegroundColor Cyan
Write-Host "  Ctrl+C - Остановить сервер"
Write-Host "  Измените файл в webapp/ → Сервер перезагружается автоматически"
Write-Host ""
Write-Host "🚀 ЗАПУСК:" -ForegroundColor Green

# Запускаем dev mode
python dev_mode.py
