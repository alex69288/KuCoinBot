"""
ПОДГОТОВКА ФИЧ ДЛЯ ML
"""
import numpy as np
import pandas as pd
from utils.helpers import calculate_ema, calculate_rsi, calculate_macd, calculate_bollinger_bands

class FeatureEngineer:
    def __init__(self):
        self.required_period = 50  # Минимальное количество данных
        
    def prepare_features(self, ohlcv_data):
        """Подготовка фич из OHLCV данных"""
        try:
            if len(ohlcv_data) < self.required_period:
                return []
                
            closes = np.array([candle[4] for candle in ohlcv_data])
            highs = np.array([candle[2] for candle in ohlcv_data])
            lows = np.array([candle[3] for candle in ohlcv_data])
            
            features = []
            
            # Ценовые фичи
            current_price = closes[-1]
            price_change_1h = (closes[-1] - closes[-4]) / closes[-4] * 100 if len(closes) >= 4 else 0
            price_change_4h = (closes[-1] - closes[-16]) / closes[-16] * 100 if len(closes) >= 16 else 0
            price_change_24h = (closes[-1] - closes[-24]) / closes[-24] * 100 if len(closes) >= 24 else 0
            
            # SMA фичи
            sma_5 = np.mean(closes[-5:])
            sma_10 = np.mean(closes[-10:])
            sma_20 = np.mean(closes[-20:])
            sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma_20
            
            # Отношения цен к SMA
            price_sma_5_ratio = current_price / sma_5
            price_sma_20_ratio = current_price / sma_20
            price_sma_50_ratio = current_price / sma_50
            
            # EMA фичи
            ema_9 = calculate_ema(closes, 9)
            ema_21 = calculate_ema(closes, 21)
            ema_diff = (ema_9 - ema_21) / ema_21 * 100
            
            # RSI
            rsi = calculate_rsi(closes)
            
            # MACD
            macd, macd_signal = calculate_macd(closes)
            macd_histogram = macd - macd_signal
            
            # Bollinger Bands
            bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(closes)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            
            # Волатильность
            volatility_5 = np.std(closes[-5:]) / np.mean(closes[-5:]) * 100
            volatility_20 = np.std(closes[-20:]) / np.mean(closes[-20:]) * 100
            
            # High/Low отношения
            high_low_ratio_5 = (np.max(highs[-5:]) - np.min(lows[-5:])) / np.mean(closes[-5:])
            high_low_ratio_20 = (np.max(highs[-20:]) - np.min(lows[-20:])) / np.mean(closes[-20:])
            
            # Собираем все фичи
            features.extend([
                current_price,
                price_change_1h,
                price_change_4h,
                price_change_24h,
                sma_5, sma_10, sma_20, sma_50,
                price_sma_5_ratio,
                price_sma_20_ratio,
                price_sma_50_ratio,
                ema_9, ema_21, ema_diff,
                rsi,
                macd, macd_signal, macd_histogram,
                bb_middle, bb_upper, bb_lower, bb_position,
                volatility_5, volatility_20,
                high_low_ratio_5, high_low_ratio_20
            ])
            
            return features
            
        except Exception as e:
            print(f"❌ Ошибка подготовки фич: {e}")
            return []

    def get_feature_names(self):
        """Получение названий фич"""
        return [
            'current_price', 'price_change_1h', 'price_change_4h', 'price_change_24h',
            'sma_5', 'sma_10', 'sma_20', 'sma_50',
            'price_sma_5_ratio', 'price_sma_20_ratio', 'price_sma_50_ratio',
            'ema_9', 'ema_21', 'ema_diff',
            'rsi',
            'macd', 'macd_signal', 'macd_histogram',
            'bb_middle', 'bb_upper', 'bb_lower', 'bb_position',
            'volatility_5', 'volatility_20',
            'high_low_ratio_5', 'high_low_ratio_20'
        ]