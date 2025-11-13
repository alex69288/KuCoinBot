"""
Скрипт для полного удаления всех иконок кроме индикаторов сигналов из index.html
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

# Счетчики
removed_count = 0

# Удаляем все варианты иконок
for icon in icons_to_remove:
    # Паттерн 1: <span class="icon icon-{name}"><svg>...</svg></span>
    pattern1 = rf'<span class="icon icon-{icon}"><svg>\s*<use href="#icon-{icon}"></use>\s*</svg></span>\s*'
    before = len(content)
    content = re.sub(pattern1, '', content)
    after = len(content)
    if before != after:
        removed_count += 1
        print(f"  - Удалены обертки icon-{icon} (паттерн 1)")
    
    # Паттерн 2: в одной строке без переносов
    pattern2 = rf'<span class="icon icon-{icon}"><svg><use href="#icon-{icon}"></use></svg></span>'
    before = len(content)
    content = re.sub(pattern2, '', content)
    after = len(content)
    if before != after:
        removed_count += 1
        print(f"  - Удалены обертки icon-{icon} (паттерн 2)")
    
    # Паттерн 3: SVG без span обертки
    pattern3 = rf'<svg class="icon icon-svg"><use href="#icon-{icon}"></use></svg>\s*'
    before = len(content)
    content = re.sub(pattern3, '', content)
    after = len(content)
    if before != after:
        removed_count += 1
        print(f"  - Удалены SVG icon-{icon}")

# Сохраняем файл
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✓ Удалено {removed_count} типов иконок")
print(f"✓ Файл сохранен: {file_path}")
