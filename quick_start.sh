#!/bin/bash
#
# Скрипт быстрого запуска KuCoin бота
# Использование: ./quick_start.sh
#

set -e  # Выход при ошибке

echo "=================================================="
echo "   ЗАПУСК KUCOIN ТОРГОВОГО БОТА"
echo "=================================================="
echo ""

# Определяем директорию скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Рабочая директория: $SCRIPT_DIR"
echo ""

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    echo "✓ Виртуальное окружение создано"
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source venv/bin/activate
echo "✓ Виртуальное окружение активировано"
echo ""

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с необходимыми переменными окружения"
    exit 1
fi
echo "✓ Файл .env найден"
echo ""

# Устанавливаем/обновляем зависимости
echo "Проверка зависимостей..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✓ Зависимости установлены"
else
    echo "⚠ Файл requirements.txt не найден"
fi
echo ""

# Запускаем проверки
echo "Запуск предстартовых проверок..."
if [ -f "tests/run_all_checks.py" ]; then
    python tests/run_all_checks.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Проверки не прошли!"
        echo "Устраните ошибки перед запуском бота"
        exit 1
    fi
else
    echo "⚠ Скрипт проверки не найден, пропускаем..."
fi

echo ""
echo "=================================================="
echo "   ЗАПУСК БОТА"
echo "=================================================="
echo ""

# Запрашиваем режим запуска
echo "Выберите режим запуска:"
echo "1) Обычный режим (с выводом в консоль)"
echo "2) Фоновый режим (screen)"
echo "3) Фоновый режим (nohup)"
echo ""
read -p "Ваш выбор (1-3): " choice

case $choice in
    1)
        echo "Запуск в обычном режиме..."
        python main.py
        ;;
    2)
        echo "Запуск в фоновом режиме через screen..."
        if ! command -v screen &> /dev/null; then
            echo "❌ screen не установлен. Установите: apt-get install screen"
            exit 1
        fi
        
        # Проверяем, не запущена ли уже сессия
        if screen -list | grep -q "kucoin_bot"; then
            echo "⚠ Сессия kucoin_bot уже существует"
            read -p "Переподключиться к существующей сессии? (y/n): " reconnect
            if [ "$reconnect" = "y" ]; then
                screen -r kucoin_bot
            else
                echo "Используйте: screen -r kucoin_bot для подключения"
            fi
        else
            screen -dmS kucoin_bot bash -c "cd $SCRIPT_DIR && source venv/bin/activate && python main.py"
            echo "✓ Бот запущен в сессии screen: kucoin_bot"
            echo ""
            echo "Для подключения к сессии используйте:"
            echo "  screen -r kucoin_bot"
            echo ""
            echo "Для отключения от сессии: Ctrl+A, затем D"
        fi
        ;;
    3)
        echo "Запуск в фоновом режиме через nohup..."
        nohup python main.py > bot.log 2>&1 &
        PID=$!
        echo "✓ Бот запущен с PID: $PID"
        echo ""
        echo "Для просмотра логов используйте:"
        echo "  tail -f bot.log"
        echo ""
        echo "Для остановки бота:"
        echo "  kill $PID"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "✓ ГОТОВО!"
echo "=================================================="
