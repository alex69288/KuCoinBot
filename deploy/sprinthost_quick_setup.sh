#!/bin/bash
# Быстрая установка KuCoin Bot на SprintHost VDS
# Автор: GitHub Copilot для alex69288
# Дата: 2025-11-11

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 УСТАНОВКА KUCOIN TRADING BOT НА SPRINTHOST VDS       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Проверка root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Запустите скрипт от имени root: sudo bash $0"
    exit 1
fi

# Получаем IP сервера
SERVER_IP=$(curl -s ifconfig.me || echo "your-server-ip")

echo "📦 [1/8] Обновление системы..."
apt update -qq && apt upgrade -y -qq

echo "🐍 [2/8] Установка Python и зависимостей..."
apt install -y -qq python3 python3-pip python3-venv git nginx curl

echo "👤 [3/8] Создание пользователя botuser..."
if ! id "botuser" &>/dev/null; then
    useradd -m -s /bin/bash botuser
    echo "   ✅ Пользователь botuser создан"
else
    echo "   ℹ️  Пользователь botuser уже существует"
fi

echo "📥 [4/8] Клонирование репозитория..."
cd /home/botuser
if [ -d "KuCoinBot" ]; then
    echo "   ⚠️  Папка KuCoinBot уже существует, удаляем..."
    rm -rf KuCoinBot
fi
git clone -q https://github.com/alex69288/KuCoinBot.git
cd KuCoinBot

echo "🔧 [5/8] Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "📦 [6/8] Установка Python зависимостей..."
echo "   ⏳ Это займет 2-3 минуты, подождите..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "⚙️  [7/8] Создание файла конфигурации..."
cat > .env << EOF
KUCOIN_API_KEY=your_api_key_here
KUCOIN_SECRET_KEY=your_secret_key_here
KUCOIN_PASSPHRASE=your_passphrase_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
WEBAPP_URL=http://${SERVER_IP}
EOF

chown -R botuser:botuser /home/botuser/KuCoinBot

echo "🔧 [8/8] Настройка автозапуска..."

# Создание systemd сервиса
cat > /etc/systemd/system/kucoinbot.service << 'EOF'
[Unit]
Description=KuCoin Trading Bot with Web App
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/KuCoinBot
Environment="PATH=/home/botuser/KuCoinBot/venv/bin"
ExecStart=/home/botuser/KuCoinBot/venv/bin/python webapp_main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Настройка Nginx
cat > /etc/nginx/sites-available/kucoinbot << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы
    location /static/ {
        alias /home/botuser/KuCoinBot/webapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/kucoinbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации Nginx
nginx -t

# Перезапуск Nginx
systemctl restart nginx

# Включение автозапуска
systemctl daemon-reload
systemctl enable kucoinbot

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1️⃣  Настройте API ключи:"
echo "   nano /home/botuser/KuCoinBot/.env"
echo ""
echo "2️⃣  Запустите бота:"
echo "   systemctl start kucoinbot"
echo ""
echo "3️⃣  Проверьте статус:"
echo "   systemctl status kucoinbot"
echo ""
echo "4️⃣  Просмотр логов в реальном времени:"
echo "   journalctl -u kucoinbot -f"
echo ""
echo "5️⃣  Откройте в браузере:"
echo "   http://${SERVER_IP}/ping"
echo "   http://${SERVER_IP}/"
echo ""
echo "📚 Полезные команды:"
echo "   systemctl restart kucoinbot  # Перезапуск"
echo "   systemctl stop kucoinbot     # Остановка"
echo "   nano /home/botuser/KuCoinBot/.env  # Редактирование настроек"
echo ""
echo "🔒 Для настройки HTTPS с доменом:"
echo "   apt install certbot python3-certbot-nginx"
echo "   certbot --nginx -d your-domain.com"
echo ""
echo "💡 После настройки .env не забудьте перезапустить бота!"
echo ""
