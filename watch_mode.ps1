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

# Запускаем watch_mode.py
python watch_mode.py
