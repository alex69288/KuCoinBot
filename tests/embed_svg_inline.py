"""
Встраивание SVG спрайтов прямо в HTML
Это самый надежный способ - SVG будет доступен сразу
"""

from pathlib import Path

def embed_svg_in_html():
    """Встраивает SVG спрайты в начало body"""
    
    # Читаем SVG
    svg_path = Path(__file__).parent.parent / 'webapp' / 'static' / 'icons.svg'
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Читаем HTML
    html_path = Path(__file__).parent.parent / 'webapp' / 'static' / 'index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Проверяем, не встроен ли уже SVG
    if '<!-- INLINE SVG SPRITES -->' in html_content:
        print("[INFO] SVG спрайты уже встроены в HTML")
        return False
    
    # Ищем <body> и вставляем SVG сразу после него
    body_tag = '<body>'
    if body_tag in html_content:
        # Формируем вставку
        svg_inline = f'{body_tag}\n  <!-- INLINE SVG SPRITES -->\n  {svg_content}\n  <!-- END INLINE SVG SPRITES -->\n\n'
        
        # Заменяем
        html_content = html_content.replace(body_tag, svg_inline, 1)
        
        # Сохраняем
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("[OK] SVG спрайты встроены в HTML")
        return True
    else:
        print("[ERROR] Тег <body> не найден в HTML")
        return False

def update_icon_hrefs():
    """Обновляет href в иконках - убирает путь к файлу, оставляет только #id"""
    
    html_path = Path(__file__).parent.parent / 'webapp' / 'static' / 'index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Заменяем /static/icons.svg# на просто #
    updated_content = html_content.replace('href="/static/icons.svg#', 'href="#')
    
    # Подсчитываем замены
    count = html_content.count('href="/static/icons.svg#')
    
    # Сохраняем
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"[OK] Обновлено {count} ссылок на иконки")
    return count

if __name__ == "__main__":
    print("[INFO] Встраивание SVG спрайтов в HTML...\n")
    
    try:
        # Шаг 1: Встраиваем SVG
        embedded = embed_svg_in_html()
        
        # Шаг 2: Обновляем ссылки
        if embedded:
            count = update_icon_hrefs()
            print(f"\n[SUCCESS] Готово!")
            print(f"  - SVG спрайты встроены в HTML")
            print(f"  - Обновлено {count} ссылок")
            print(f"  - Формат: <use href='#icon-name'>")
        else:
            print("\n[INFO] SVG уже встроен, обновляем только ссылки...")
            count = update_icon_hrefs()
            print(f"[OK] Обновлено {count} ссылок")
            
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
