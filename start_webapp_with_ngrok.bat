@echo off
echo ================================================
echo   Запуск Web App с ngrok для Telegram
echo ================================================
echo.

REM Проверяем, установлен ли ngrok
where ngrok >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] ngrok не установлен!
    echo.
    echo Скачайте ngrok:
    echo 1. Перейдите на https://ngrok.com/download
    echo 2. Скачайте ngrok для Windows
    echo 3. Распакуйте в любую папку
    echo 4. Добавьте путь к ngrok в PATH или поместите рядом с этим скриптом
    echo.
    pause
    exit /b 1
)

echo [1/3] Запуск Web App сервера...
start "WebApp Server" cmd /k "python -m webapp.server"
timeout /t 3 >nul

echo [2/3] Запуск ngrok туннеля...
start "ngrok" cmd /k "ngrok http 8000"
timeout /t 5 >nul

echo.
echo ================================================
echo   Web App сервер запущен!
echo ================================================
echo.
echo Откройте окно ngrok и найдите HTTPS URL
echo Пример: https://abc123.ngrok.io
echo.
echo Следующие шаги:
echo 1. Скопируйте HTTPS URL из окна ngrok
echo 2. Добавьте в .env файл: WEBAPP_URL=https://ваш-url.ngrok.io
echo 3. Перезапустите бота: python main.py
echo 4. Откройте Web App в Telegram!
echo.
echo Для остановки закройте оба окна (WebApp Server и ngrok)
echo.
pause
