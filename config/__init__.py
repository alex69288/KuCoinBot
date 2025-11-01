"""
КОНФИГУРАЦИЯ ПРОЕКТА
"""
from .constants import *
from .settings import SettingsManager

__all__ = ['TRADING_PAIRS', 'STRATEGIES', 'DEFAULT_SETTINGS', 'DEFAULT_ML_SETTINGS', 
           'DEFAULT_RISK_SETTINGS', 'TIMEFRAMES', 'MESSAGES', 'SettingsManager']