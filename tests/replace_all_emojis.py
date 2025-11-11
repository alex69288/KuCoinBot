"""Скрипт для замены эмодзи во всех HTML файлах"""
import os
import glob

# Маппинг эмодзи на CSS классы
EMOJI_MAP = {
    '🤖': '<span class="icon icon-robot"></span>',
    '📊': '<span class="icon icon-chart"></span>',
    '💰': '<span class="icon icon-money"></span>',
    '💵': '<span class="icon icon-money"></span>',
    '💸': '<span class="icon icon-card"></span>',
    '📈': '<span class="icon icon-trend-up"></span>',
    '📉': '<span class="icon icon-trend-down"></span>',
    '⚠️': '<span class="icon icon-warning"></span>',
    '⚠': '<span class="icon icon-warning"></span>',
    '✅': '<span class="icon icon-check"></span>',
    '❌': '<span class="icon icon-close"></span>',
    '⏸': '<span class="icon icon-pause"></span>',
    '⏸️': '<span class="icon icon-pause"></span>',
    '▶️': '<span class="icon icon-play"></span>',
    '▶': '<span class="icon icon-play"></span>',
    '🔄': '<span class="icon icon-refresh"></span>',
    '📋': '<span class="icon icon-list"></span>',
    '⚙️': '<span class="icon icon-settings"></span>',
    '⚙': '<span class="icon icon-settings"></span>',
    '💼': '<span class="icon icon-wallet"></span>',
    '🎯': '<span class="icon icon-target"></span>',
    '🔔': '<span class="icon icon-bell"></span>',
    '📱': '<span class="icon icon-phone"></span>',
    '💳': '<span class="icon icon-card"></span>',
    '🛑': '<span class="icon icon-stop"></span>',
    '⏹': '<span class="icon icon-stop"></span>',
    '🏠': '<span class="icon icon-home"></span>',
    '🎮': '<span class="icon icon-gamepad"></span>',
    '📜': '<span class="icon icon-document"></span>',
    '📍': '<span class="icon icon-pin"></span>',
    '🗑️': '<span class="icon icon-trash"></span>',
    '🗑': '<span class="icon icon-trash"></span>',
    '💾': '<span class="icon icon-save"></span>',
    '🛡️': '<span class="icon icon-shield"></span>',
    '🛡': '<span class="icon icon-shield"></span>',
    '🔧': '<span class="icon icon-wrench"></span>',
    '🟢': '<span class="icon icon-circle-green"></span>',
    '🔴': '<span class="icon icon-circle-red"></span>',
    '🟡': '<span class="icon icon-circle-yellow"></span>',
    '⚪': '<span class="icon icon-circle-white"></span>',
    '📭': '<span class="icon icon-inbox"></span>',
    '🪙': '<span class="icon icon-money"></span>',
    '💹': '<span class="icon icon-chart"></span>',
    '🔍': '<span class="icon icon-target"></span>',
    '🔑': '<span class="icon icon-card"></span>',
    '🚀': '<span class="icon icon-play"></span>',
}

def replace_emojis_in_file(file_path):
    """Заменить все эмодзи в файле на CSS классы"""
    print(f"\nОбработка файла: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements_count = 0
    
    # Заменяем каждое эмодзи
    for emoji, css_class in EMOJI_MAP.items():
        if emoji in content:
            count = content.count(emoji)
            content = content.replace(emoji, css_class)
            replacements_count += count
            print(f"  Заменено {count}x: {emoji}")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Файл обновлен. Всего замен: {replacements_count}")
        return True
    else:
        print("  Эмодзи не найдены")
        return False

def main():
    """Основная функция"""
    base_path = r'c:\Users\user\Documents\Scripts\KuCoinBotV4Copilot'
    
    # Найти все HTML файлы
    html_files = []
    html_files.extend(glob.glob(os.path.join(base_path, 'webapp', 'static', '*.html')))
    html_files.extend(glob.glob(os.path.join(base_path, 'docs', '*.html')))
    
    print("=== Замена эмодзи во всех HTML файлах ===")
    print(f"Найдено файлов: {len(html_files)}")
    
    updated_files = 0
    for html_file in html_files:
        if replace_emojis_in_file(html_file):
            updated_files += 1
    
    print(f"\n✓ Обработка завершена!")
    print(f"  Обновлено файлов: {updated_files}")
    print(f"  Без изменений: {len(html_files) - updated_files}")

if __name__ == '__main__':
    main()
