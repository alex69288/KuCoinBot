"""
ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_ema(prices, period):
    """Расчет EMA"""
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]

def calculate_rsi(prices, period=14):
    """Расчет RSI"""
    try:
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return 50

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Расчет MACD"""
    try:
        exp1 = pd.Series(prices).ewm(span=fast).mean()
        exp2 = pd.Series(prices).ewm(span=slow).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=signal).mean()
        return macd.iloc[-1], macd_signal.iloc[-1]
    except:
        return 0, 0

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Расчет Bollinger Bands"""
    try:
        series = pd.Series(prices)
        sma = series.rolling(period).mean()
        std = series.rolling(period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return sma.iloc[-1], upper_band.iloc[-1], lower_band.iloc[-1]
    except:
        return 0, 0, 0

def format_price(price):
    """Форматирование цены"""
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.6f}"

def format_percent(value):
    """Форматирование процентов"""
    return f"{value:+.2f}%"

def is_new_day(last_reset_date):
    """Проверка наступления нового дня"""
    return datetime.now().date() != last_reset_date

def calculate_volatility(prices):
    """Расчет волатильности"""
    try:
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * 100
        return volatility
    except:
        return 0.0

def validate_number_input(value, min_val, max_val):
    """Валидация числового ввода"""
    try:
        num_value = float(value)
        return min_val <= num_value <= max_val
    except:
        return False