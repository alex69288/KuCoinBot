"""
Скрипт для ПРЯМОЙ замены иконок в HTML
Заменяет <span class="icon icon-*"></span> на правильный SVG формат
"""

import re
from pathlib import Path

def fix_icons_in_html(file_path):
    """Исправляет иконки в HTML файле"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерн для поиска: <span class="icon icon-название"><svg>...</svg></span>
    # или <span class="icon icon-название"></span>
    
    # Сначала удаляем неправильные SVG если они есть
    content = re.sub(
        r'<span class="icon (icon-[\w-]+)"><svg><use href="#\1"></use></svg></span>',
        r'<span class="icon \1"></span>',
        content
    )
    
    # Теперь заменяем все на правильный формат
    def replace_icon(match):
        full_classes = match.group(1)
        # Находим класс icon-*
        icon_match = re.search(r'icon-([\w-]+)', full_classes)
        if icon_match:
            icon_name = icon_match.group(1)
            return f'<span class="{full_classes}"><svg><use href="/static/icons.svg#icon-{icon_name}"></use></svg></span>'
        return match.group(0)
    
    # Паттерн для замены всех иконок
    pattern = r'<span class="([^"]*\bicon\b[^"]*\bicon-[\w-]+[^"]*)">(?:<svg>.*?</svg>)?</span>'
    
    updated_content = re.sub(pattern, replace_icon, content)
    
    # Подсчитываем количество замен
    icon_count = len(re.findall(r'<span class="[^"]*\bicon-[\w-]+[^"]*">', updated_content))
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return icon_count

if __name__ == "__main__":
    index_path = Path(__file__).parent.parent / 'webapp' / 'static' / 'index.html'
    
    print("[INFO] Исправление иконок в index.html...")
    print(f"[INFO] Файл: {index_path}")
    
    try:
        count = fix_icons_in_html(index_path)
        print(f"\n[OK] Обработано иконок: {count}")
        print("[OK] Формат: <span class='icon icon-*'><svg><use href='/static/icons.svg#icon-*'></use></svg></span>")
        print("\n[OK] Готово!")
        
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
