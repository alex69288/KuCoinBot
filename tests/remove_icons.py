"""
Скрипт для удаления всех иконок кроме индикаторов сигналов из index.html
"""
import re

# Путь к файлу
file_path = r"c:\Users\user\Documents\Scripts\KuCoinBotV4Copilot\webapp\static\index.html"

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Список иконок, которые нужно удалить (все кроме icon-circle-*)
icons_to_remove = [
    'robot', 'chart', 'money', 'trend-up', 'trend-down', 'warning', 'check', 'close',
    'pause', 'play', 'refresh', 'list', 'settings', 'wallet', 'target', 'bell',
    'phone', 'card', 'stop', 'home', 'gamepad', 'document', 'pin', 'trash',
    'save', 'shield', 'wrench', 'inbox', 'ema'
]

# Паттерны для замены
patterns = []
for icon in icons_to_remove:
    # Удаляем обертки <span class="icon icon-{name}"><svg><use href="#icon-{name}"></use></svg></span>
    pattern = rf'<span class="icon icon-{icon}"><svg><use href="#icon-{icon}"></use></svg></span>\s*'
    patterns.append((pattern, ''))
    
    # Удаляем обертки в inline стиле
    pattern = rf'<svg class="icon icon-svg"><use href="#icon-{icon}"></use></svg>\s*'
    patterns.append((pattern, ''))

# Применяем замены
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Сохраняем файл
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Удалены все иконки кроме индикаторов сигналов")
print(f"✓ Файл сохранен: {file_path}")
