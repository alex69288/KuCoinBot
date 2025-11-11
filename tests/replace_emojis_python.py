"""Скрипт для замены эмодзи в Python логах на текстовые префиксы"""
import re

# Маппинг эмодзи на текстовые префиксы для логов
EMOJI_MAP_LOGS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    '🔍': '[INFO]',
    '📂': '[DIR]',
    '🚀': '[START]',
    '🛑': '[STOP]',
    '⚙️': '[CONFIG]',
    '⚙': '[CONFIG]',
    '📴': '[CLOSE]',
    '🗑️': '[DELETE]',
    '🗑': '[DELETE]',
    '🤖': '[ML]',
    '📈': '[ANALYSIS]',
    '🛡️': '[RISK]',
    '🛡': '[RISK]',
    '🌐': '[WEB]',
}

def replace_emojis_in_python_file(file_path):
    """Заменить все эмодзи в Python файле на текстовые префиксы"""
    print(f"Обработка файла: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements_count = 0
    
    # Заменяем каждое эмодзи
    for emoji, prefix in EMOJI_MAP_LOGS.items():
        if emoji in content:
            count = content.count(emoji)
            content = content.replace(emoji, prefix)
            replacements_count += count
            print(f"  Заменено {count}x: {emoji} -> {prefix}")
    
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
    python_file = r'c:\Users\user\Documents\Scripts\KuCoinBotV4Copilot\webapp\server.py'
    
    print("=== Замена эмодзи в Python файлах ===\n")
    
    if replace_emojis_in_python_file(python_file):
        print("\n✓ Замена завершена успешно!")
    else:
        print("\n! Эмодзи не найдены или уже заменены")

if __name__ == '__main__':
    main()
