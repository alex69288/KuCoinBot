# 🚀 КОМАНДЫ ДЛЯ ЗАПУСКА БОТА НА СЕРВЕРЕ

## Подключение к серверу
```bash
ssh root@box-870236.sprintbox.ru -p 5823
```
Пароль: `Ioy@eN^7rHmV`

---

## Обновление кода с GitHub
```bash
cd /home/botuser/KuCoinBot
git pull
```

---

## Запуск проверок
```bash
cd /home/botuser/KuCoinBot
source venv/bin/activate
python tests/run_all_checks.py
```

---

## Запуск бота (простой способ)
```bash
cd /home/botuser/KuCoinBot
source venv/bin/activate
python main.py
```

---

## Запуск бота в фоне (screen)
```bash
cd /home/botuser/KuCoinBot
chmod +x quick_start.sh
./quick_start.sh
# Выберите вариант 2 для запуска через screen
```

**Важные команды screen:**
- Подключиться к сессии: `screen -r kucoin_bot`
- Отключиться от сессии: `Ctrl+A`, затем `D`
- Список сессий: `screen -ls`

---

## Просмотр логов
```bash
# Логи бота
tail -f /home/botuser/KuCoinBot/logs/bot.log

# Или если запущен через quick_start.sh вариант 3
tail -f /home/botuser/KuCoinBot/bot.log
```

---

## Остановка бота
```bash
# Если запущен через screen
screen -r kucoin_bot
# Затем нажмите Ctrl+C

# Или принудительно
pkill -f "python main.py"
```

---

## Полная последовательность для первого запуска

```bash
# 1. Подключаемся к серверу
ssh root@box-870236.sprintbox.ru -p 5823

# 2. Переходим в директорию
cd /home/botuser/KuCoinBot

# 3. Обновляем код
git pull

# 4. Активируем окружение
source venv/bin/activate

# 5. Запускаем проверки
python tests/run_all_checks.py

# 6. Если все OK, запускаем бота
python main.py
```

---

## Telegram команды

После запуска бота отправьте ему в Telegram:
- `/start` - Начать работу
- `/status` - Посмотреть статус
- `/settings` - Настройки

---

## 🔥 БЫСТРЫЙ СТАРТ (одна команда)

```bash
ssh root@box-870236.sprintbox.ru -p 5823 "cd /home/botuser/KuCoinBot && source venv/bin/activate && python tests/run_all_checks.py && screen -dmS kucoin_bot bash -c 'cd /home/botuser/KuCoinBot && source venv/bin/activate && python main.py'"
```

Затем подключитесь к сессии:
```bash
ssh root@box-870236.sprintbox.ru -p 5823
screen -r kucoin_bot
```
