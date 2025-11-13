"""
КОНСТАНТЫ ДЛЯ ИКОНОК И ЭМОДЗИ v0.1.15
Централизованное хранилище всех визуальных элементов проекта
"""

# ==================== ОСНОВНЫЕ СИМВОЛЫ ====================
class Icons:
    """Текстовые иконки для Telegram и логирования"""
    
    # Статусы
    SUCCESS = "✓"  # Галочка
    ERROR = "✗"  # Крестик
    WARNING = "⚠"  # Предупреждение
    INFO = "ℹ"  # Информация
    
    # Торговые символы  
    UP = "↑"  # Рост
    DOWN = "↓"  # Падение
    NEUTRAL = "−"  # Нейтрально
    
    # Действия
    PLAY = "▶"  # Запуск
    PAUSE = "⏸"  # Пауза
    STOP = "■"  # Остановка
    REFRESH = "⟳"  # Обновление
    
    # Метки
    BULLET = "•"  # Пункт списка
    ARROW = "→"  # Стрелка
    STAR = "★"  # Звезда
    PIN = "📍"  # Позиция


class Emoji:
    """Эмодзи для Telegram бота - остаются для совместимости"""
    
    # Статусы бота
    ROBOT = "🤖"
    ONLINE = "🟢"
    OFFLINE = "🔴"
    PAUSE = "🟡"
    
    # Финансы
    MONEY = "💰"
    CHART = "📊"
    TREND_UP = "📈"
    TREND_DOWN = "📉"
    CARD = "💳"
    
    # Действия
    SETTINGS = "⚙️"
    TARGET = "🎯"
    BELL = "🔔"
    SAVE = "💾"
    TRASH = "🗑️"
    
    # Информация
    INFO = "ℹ️"
    WARNING = "⚠️"
    CHECK = "✅"
    CROSS = "❌"
    
    # Документы
    DOCUMENT = "📄"
    LIST = "📋"
    PIN = "📌"


class Colors:
    """ANSI цветовые коды для консольного вывода"""
    
    # Основные цвета
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Цвета текста
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Яркие цвета
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"
    
    # Фоны
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


# Утилиты для форматирования
def format_status(status: str, use_emoji: bool = True) -> str:
    """
    Форматирует статус с соответствующей иконкой
    
    Args:
        status: Статус (success, error, warning, info)
        use_emoji: Использовать эмодзи (True) или текстовые иконки (False)
    
    Returns:
        Отформатированная строка со статусом
    """
    if use_emoji:
        icons = {
            'success': Emoji.CHECK,
            'error': Emoji.CROSS,
            'warning': Emoji.WARNING,
            'info': Emoji.INFO
        }
    else:
        icons = {
            'success': Icons.SUCCESS,
            'error': Icons.ERROR,
            'warning': Icons.WARNING,
            'info': Icons.INFO
        }
    
    return icons.get(status.lower(), Icons.BULLET)


def format_trend(value: float, use_emoji: bool = True) -> str:
    """
    Форматирует тренд с соответствующей иконкой
    
    Args:
        value: Числовое значение тренда
        use_emoji: Использовать эмодзи (True) или текстовые иконки (False)
    
    Returns:
        Иконка тренда
    """
    if use_emoji:
        if value > 0:
            return Emoji.TREND_UP
        elif value < 0:
            return Emoji.TREND_DOWN
        else:
            return Icons.NEUTRAL
    else:
        if value > 0:
            return Icons.UP
        elif value < 0:
            return Icons.DOWN
        else:
            return Icons.NEUTRAL


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Добавляет ANSI цвета к тексту для консольного вывода
    
    Args:
        text: Текст для раскраски
        color: Название цвета из класса Colors
        bold: Сделать текст жирным
    
    Returns:
        Раскрашенный текст
    """
    color_code = getattr(Colors, color.upper(), Colors.RESET)
    bold_code = Colors.BOLD if bold else ""
    
    return f"{bold_code}{color_code}{text}{Colors.RESET}"


# Примеры использования
if __name__ == "__main__":
    print("=== ДЕМОНСТРАЦИЯ ИКОНОК ===\n")
    
    print("Статусы:")
    print(f"  {format_status('success')} Успех")
    print(f"  {format_status('error')} Ошибка")
    print(f"  {format_status('warning')} Предупреждение")
    print(f"  {format_status('info')} Информация")
    
    print("\nТренды:")
    print(f"  {format_trend(1.5)} Рост")
    print(f"  {format_trend(-1.5)} Падение")
    print(f"  {format_trend(0)} Нейтрально")
    
    print("\nЦветной текст:")
    print(f"  {colorize('Успех', 'green', bold=True)}")
    print(f"  {colorize('Ошибка', 'red', bold=True)}")
    print(f"  {colorize('Предупреждение', 'yellow', bold=True)}")
    print(f"  {colorize('Информация', 'cyan', bold=True)}")
