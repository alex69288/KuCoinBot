"""
ЛОГГИРОВАНИЕ
"""
import logging
import os
from datetime import datetime

def setup_logger():
    """Настройка логгера"""
    # Создаем папку для логов если ее нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый логгер
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Консольный логгер
    console_handler = logging.StreamHandler()
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