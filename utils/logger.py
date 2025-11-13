"""
ЛОГГИРОВАНИЕ v0.1.16
Система логирования без иконок
"""
import logging
import os
import sys
from datetime import datetime

def setup_logger():
    """Настройка логгера"""
    # Создаем папку для логов если ее нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Простое форматирование
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый логгер с UTF-8 кодировкой
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Консольный логгер с правильной кодировкой для Windows
    # На Windows используем sys.stdout/stderr, которые уже переконфигурированы в entry points
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Настройка основного логгера
    logger = logging.getLogger('TradingBot')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем глобальный логгер
logger = setup_logger()

def log_info(message):
    """Логирование информационного сообщения"""
    logger.info(message)

def log_error(message):
    """Логирование ошибки"""
    logger.error(message)

def log_warning(message):
    """Логирование предупреждения"""
    logger.warning(message)

def log_debug(message):
    """Логирование отладочной информации"""
    logger.debug(message)

def log_separator(char="=", length=80):
    """Вывод разделительной линии для лучшей читаемости"""
    logger.info(char * length)

def log_section(title, char="=", length=80):
    """Вывод заголовка секции с разделителями"""
    padding = (length - len(title) - 4) // 2
    separator = char * length
    header = f"{char * padding} {title} {char * padding}"
    if len(header) < length:
        header += char
    logger.info(separator)
    logger.info(header)
    logger.info(separator)

def log_empty_line():
    """Вывод пустой строки для разделения"""
    logger.info("")