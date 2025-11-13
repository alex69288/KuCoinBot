"""
Скрипт для обновления всех иконок в index.html на новые SVG иконки
Заменяет старый формат <span class="icon icon-*"></span> на 
<span class="icon icon-*"><svg><use href="/static/icons.svg#icon-*"/></svg></span>
"""

import re
from pathlib import Path

def update_icons_in_html(file_path):
    """Обновляет все иконки в HTML файле"""
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерн для поиска иконок: <span class="icon icon-название">...</span>
    # Ищем все варианты с закрывающим тегом или самозакрывающимся
    pattern = r'<span class="icon (icon-[\w-]+)">(?:</span>|([^<]*))'
    
    def replace_icon(match):
        icon_class = match.group(1)
        icon_name = icon_class.replace('icon-', '')
        
        # Если иконка уже содержит SVG, не трогаем её
        if match.group(2) and 'svg' in match.group(2).lower():
            return match.group(0)
        
        # Создаем новую иконку с SVG
        return f'<span class="icon {icon_class}"><svg><use href="/static/icons.svg#icon-{icon_name}"/></svg></span>'
    
    # Заменяем все иконки
    updated_content = re.sub(pattern, replace_icon, content)
    
    # Подсчитываем количество замен
    original_count = len(re.findall(pattern, content))
    
    # Создаем бэкап
    backup_path = file_path.parent / f"{file_path.stem}.backup{file_path.suffix}"
    if not backup_path.exists():
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Создан бэкап: {backup_path.name}")
    
    # Сохраняем обновленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return original_count

if __name__ == "__main__":
    # Путь к index.html
    index_path = Path(__file__).parent.parent / 'webapp' / 'static' / 'index.html'
    
    if not index_path.exists():
        print(f"[ERROR] Файл не найден: {index_path}")
        exit(1)
    
    print("[INFO] Обновление иконок в index.html...")
    print(f"[INFO] Файл: {index_path}")
    
    try:
        count = update_icons_in_html(index_path)
        print(f"\n[OK] Обновлено иконок: {count}")
        print(f"[OK] Файл сохранен: {index_path.name}")
        print("\n[INFO] Новый формат иконок:")
        print('  <span class="icon icon-*"><svg><use href="/static/icons.svg#icon-*"/></svg></span>')
        print("\n[OK] Готово!")
        
    except Exception as e:
        print(f"\n[ERROR] Ошибка обновления: {e}")
        exit(1)
