"""
СКРИПТ ДЛЯ БЭКТЕСТИНГА СТРАТЕГИЙ НА ИСТОРИЧЕСКИХ ДАННЫХ
"""
import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from strategies.ema_ml import EmaMlStrategy
from strategies.price_action import PriceActionStrategy
from strategies.macd_rsi import MacdRsiStrategy
from strategies.bollinger import BollingerStrategy
from utils.helpers import calculate_ema
try:
    from utils.logger import log_info, log_error
except ImportError:
    # Fallback для случаев, когда logger недоступен
    def log_info(msg):
        print(f"[INFO] {msg}")
    def log_error(msg):
        print(f"[ERROR] {msg}")


class BacktestEngine:
    """Движок для бэктестинга стратегий"""
    
    def __init__(self, initial_balance=1000.0, taker_fee=0.001, size_percent=0.1):
        """
        Инициализация бэктест-движка
        
        Args:
            initial_balance: Начальный баланс в USDT
            taker_fee: Комиссия биржи (0.1% для KuCoin)
            size_percent: Размер ставки в процентах от баланса (0.1 = 10%)
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.taker_fee = taker_fee
        self.size_percent = size_percent
        self.position = None  # 'long' или None
        self.entry_price = 0
        self.entry_balance = 0
        self.trades = []
        self.equity_curve = []
        
    def reset(self):
        """Сброс состояния для нового теста"""
        self.balance = self.initial_balance
        self.position = None
        self.entry_price = 0
        self.entry_balance = 0
        self.trades = []
        self.equity_curve = []
    
    def open_position(self, price, size_percent=None):
        """Открытие позиции"""
        if self.position is not None:
            return False
        
        if size_percent is None:
            size_percent = self.size_percent
        
        position_size = self.balance * size_percent
        if position_size < 0.1:  # Минимальный размер позиции
            return False
        
        self.position = 'long'
        self.entry_price = price
        self.entry_balance = position_size
        return True
    
    def close_position(self, price):
        """Закрытие позиции с расчетом прибыли"""
        if self.position is None:
            return None
        
        # Расчет прибыли
        profit_percent = ((price - self.entry_price) / self.entry_price) * 100
        gross_profit = self.entry_balance * (profit_percent / 100)
        
        # Комиссии (вход и выход)
        fees = self.entry_balance * self.taker_fee * 2
        net_profit = gross_profit - fees
        
        # Обновление баланса
        self.balance += net_profit
        
        # Сохранение сделки
        trade = {
            'entry_price': self.entry_price,
            'exit_price': price,
            'entry_balance': self.entry_balance,
            'profit_percent': profit_percent,
            'net_profit': net_profit,
            'fees': fees,
            'balance_after': self.balance
        }
        self.trades.append(trade)
        
        # Сброс позиции
        self.position = None
        self.entry_price = 0
        self.entry_balance = 0
        
        return trade
    
    def get_market_data(self, ohlcv_data, index):
        """Получение рыночных данных для индекса"""
        if index < 50:  # Нужно минимум 50 свечей для расчета индикаторов
            return None
        
        closes = [candle[4] for candle in ohlcv_data[:index+1]]
        current_price = closes[-1]
        
        # Расчет EMA
        fast_ema = calculate_ema(closes, 9)
        slow_ema = calculate_ema(closes, 21)
        ema_diff_percent = (fast_ema - slow_ema) / slow_ema
        
        # Изменение цены за 24 часа
        price_change_24h = 0
        if len(closes) >= 24:
            price_24h_ago = closes[-24]
            price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        return {
            'fast_ema': fast_ema,
            'slow_ema': slow_ema,
            'ema_diff_percent': ema_diff_percent,
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'ohlcv': ohlcv_data[:index+1]
        }
    
    def run_backtest(self, strategy, symbol, timeframe='1h', days=30):
        """
        Запуск бэктестинга
        
        Args:
            strategy: Экземпляр стратегии
            symbol: Торговая пара (например, 'BTC/USDT')
            timeframe: Таймфрейм ('1h', '4h', '1d')
            days: Количество дней для тестирования
        """
        self.reset()
        strategy.position = None
        strategy.entry_price = 0
        
        log_info(f"🚀 Запуск бэктестинга для {strategy.name}")
        log_info(f"📊 Пара: {symbol}, Таймфрейм: {timeframe}, Период: {days} дней")
        log_info(f"💰 Начальный баланс: {self.initial_balance:.2f} USDT")
        log_info(f"💰 Размер ставки: {self.size_percent * 100:.1f}% от баланса")
        
        # Показываем ключевые параметры стратегии
        if hasattr(strategy, 'settings'):
            settings = strategy.settings
            if 'take_profit_percent' in settings and settings.get('take_profit_usdt', 0) == 0:
                log_info(f"🎯 Take Profit: {settings.get('take_profit_percent', 2.0):.2f}%")
            elif settings.get('take_profit_usdt', 0) > 0:
                log_info(f"🎯 Take Profit: {settings.get('take_profit_usdt', 0):.4f} USDT")
            log_info(f"🛑 Stop Loss: {settings.get('stop_loss_percent', 1.5):.1f}%")
            if 'ema_threshold' in settings:
                log_info(f"📊 EMA Threshold: {settings.get('ema_threshold', 0.005) * 100:.2f}%")
        
        # Подключение к бирже
        try:
            exchange = ccxt.kucoin({
                'enableRateLimit': True,
                'rateLimit': 300,
            })
            
            # Расчет количества свечей
            limit = days * 24 if timeframe == '1h' else days * 6 if timeframe == '4h' else days
            
            log_info(f"📥 Загрузка исторических данных ({limit} свечей)...")
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv or len(ohlcv) < 50:
                log_error("❌ Недостаточно данных для бэктестинга")
                return None
            
            log_info(f"✅ Загружено {len(ohlcv)} свечей")
            
            # Симуляция ML (для EMA+ML стратегии)
            # Используем более реалистичные значения ML
            ml_confidence = 0.6  # Более высокое значение для лучших сигналов
            ml_signal = "🟢 БЫЧЬИЙ" if ml_confidence > 0.5 else "🔴 МЕДВЕЖИЙ"
            
            # Основной цикл бэктестинга
            log_info("🔄 Запуск бэктестинга...")
            
            # Добавляем счетчик для диагностики
            total_iterations = len(ohlcv) - 50
            log_info(f"📊 Всего итераций для обработки: {total_iterations}")
            
            for i in range(50, len(ohlcv)):
                market_data = self.get_market_data(ohlcv, i)
                if not market_data:
                    continue
                
                current_price = market_data['current_price']
                candle_timestamp = ohlcv[i][0]  # Timestamp свечи
                
                # Получаем сигнал от стратегии
                # Для открытой позиции используем сохраненный размер, для новой - рассчитываем
                if self.position == 'long':
                    # Если позиция открыта, используем сохраненный размер из стратегии
                    if hasattr(strategy, 'position_size_usdt') and strategy.position_size_usdt > 0:
                        position_size = strategy.position_size_usdt
                    else:
                        position_size = self.entry_balance
                else:
                    position_size = self.balance * self.size_percent
                
                # Временно переопределяем time.time() для правильной работы защиты от частых сигналов
                # Используем timestamp свечи вместо реального времени
                original_time = time.time
                time.time = lambda: candle_timestamp / 1000  # Конвертируем мс в секунды
                
                try:
                    signal = strategy.calculate_signal(
                        market_data, 
                        ml_confidence=ml_confidence,
                        ml_signal=ml_signal,
                        position_size_usdt=position_size
                    )
                finally:
                    # Восстанавливаем оригинальный time.time
                    time.time = original_time
                
                # Обработка сигналов
                if signal == 'buy' and self.position is None:
                    if self.open_position(current_price):
                        # Сохраняем размер позиции в стратегии ДО обновления позиции
                        if hasattr(strategy, 'position_size_usdt'):
                            strategy.position_size_usdt = self.entry_balance
                        # Устанавливаем позицию в стратегии ПЕРЕД обновлением
                        strategy.position = 'long'
                        strategy.entry_price = current_price
                        if hasattr(strategy, 'highest_price_since_entry'):
                            strategy.highest_price_since_entry = current_price
                        if hasattr(strategy, 'position_opened_at'):
                            strategy.position_opened_at = candle_timestamp / 1000
                        strategy.update_position_info('buy', current_price)
                        log_info(f"🟢 BUY: {current_price:.2f} USDT, размер позиции: {self.entry_balance:.2f} USDT")
                
                elif signal == 'sell' and self.position == 'long':
                    trade = self.close_position(current_price)
                    if trade:
                        strategy.update_position_info('sell', current_price)
                        profit_emoji = "✅" if trade['net_profit'] > 0 else "❌"
                        
                        # Правильное определение причины закрытия
                        # Получаем настройки SL из стратегии
                        sl_percent = 1.5  # по умолчанию
                        if hasattr(strategy, 'settings'):
                            sl_percent = strategy.settings.get('stop_loss_percent', 1.5)
                        
                        # Учитываем комиссии при определении SL
                        # Комиссии: 0.2% (0.1% вход + 0.1% выход)
                        net_loss_percent = trade['profit_percent'] - 0.2  # грубая оценка
                        
                        if trade['net_profit'] > 0:
                            reason = "TP"
                        elif abs(net_loss_percent) >= sl_percent * 0.8:  # Учитываем погрешность
                            reason = "SL"
                        else:
                            reason = "Закрытие"
                        
                        log_info(f"{profit_emoji} SELL: {current_price:.2f} USDT | "
                               f"Прибыль: {trade['profit_percent']:.2f}% ({trade['net_profit']:.2f} USDT) | {reason}")
                
                # Диагностика для открытой позиции (каждые 100 свечей)
                elif self.position == 'long' and i % 100 == 0:
                    profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
                    if hasattr(strategy, 'settings'):
                        tp = strategy.settings.get('take_profit_percent', 2.0)
                        sl = strategy.settings.get('stop_loss_percent', 1.5)
                        log_info(f"📊 Позиция открыта: цена={current_price:.2f}, прибыль={profit_percent:.2f}%, TP={tp:.2f}%, SL={sl:.1f}%")
                
                # Обновление кривой баланса
                current_balance = self.balance
                if self.position == 'long':
                    # Расчет текущей прибыли
                    profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
                    current_balance = self.balance + (self.entry_balance * (profit_percent / 100))
                
                self.equity_curve.append({
                    'timestamp': ohlcv[i][0],
                    'balance': current_balance,
                    'price': current_price
                })
            
            # Закрытие открытой позиции в конце
            if self.position == 'long':
                final_price = ohlcv[-1][4]
                trade = self.close_position(final_price)
                if trade:
                    log_info(f"🔚 Финальная позиция закрыта: {trade['profit_percent']:.2f}%")
            
            # Расчет статистики
            stats = self.calculate_statistics()
            
            log_info("=" * 60)
            log_info("📊 РЕЗУЛЬТАТЫ БЭКТЕСТИНГА")
            log_info("=" * 60)
            log_info(f"💰 Начальный баланс: {self.initial_balance:.2f} USDT")
            log_info(f"💰 Конечный баланс: {self.balance:.2f} USDT")
            log_info(f"📈 Прибыль: {stats['total_profit']:.2f} USDT ({stats['total_profit_percent']:.2f}%)")
            log_info(f"📊 Всего сделок: {stats['total_trades']}")
            log_info(f"✅ Прибыльных: {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
            log_info(f"❌ Убыточных: {stats['losing_trades']} ({stats['loss_rate']:.1f}%)")
            log_info(f"📊 Средняя прибыль: {stats['avg_profit']:.2f} USDT")
            log_info(f"📊 Максимальная прибыль: {stats['max_profit']:.2f} USDT")
            log_info(f"📊 Максимальный убыток: {stats['max_loss']:.2f} USDT")
            log_info(f"📉 Максимальная просадка: {stats['max_drawdown']:.2f}%")
            log_info(f"📊 Profit Factor: {stats['profit_factor']:.2f}")
            log_info("=" * 60)
            
            return stats
            
        except Exception as e:
            log_error(f"❌ Ошибка при бэктестинге: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_statistics(self):
        """Расчет статистики бэктестинга"""
        if not self.trades:
            return {
                'total_profit': 0,
                'total_profit_percent': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'loss_rate': 0,
                'avg_profit': 0,
                'max_profit': 0,
                'max_loss': 0,
                'max_drawdown': 0,
                'profit_factor': 0
            }
        
        total_profit = self.balance - self.initial_balance
        total_profit_percent = (total_profit / self.initial_balance) * 100
        
        winning_trades = [t for t in self.trades if t['net_profit'] > 0]
        losing_trades = [t for t in self.trades if t['net_profit'] < 0]
        
        total_trades = len(self.trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        loss_rate = (len(losing_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_profit = np.mean([t['net_profit'] for t in self.trades]) if self.trades else 0
        max_profit = max([t['net_profit'] for t in self.trades]) if self.trades else 0
        max_loss = min([t['net_profit'] for t in self.trades]) if self.trades else 0
        
        # Расчет максимальной просадки
        max_drawdown = 0
        peak = self.initial_balance
        for point in self.equity_curve:
            if point['balance'] > peak:
                peak = point['balance']
            drawdown = ((peak - point['balance']) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Profit Factor
        total_gains = sum([t['net_profit'] for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t['net_profit'] for t in losing_trades])) if losing_trades else 0
        profit_factor = total_gains / total_losses if total_losses > 0 else float('inf') if total_gains > 0 else 0
        
        return {
            'total_profit': total_profit,
            'total_profit_percent': total_profit_percent,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'avg_profit': avg_profit,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'trades': self.trades
        }


def main():
    """Главная функция для запуска бэктестинга"""
    print("=" * 60)
    print("🧪 БЭКТЕСТИНГ СТРАТЕГИЙ")
    print("=" * 60)
    print()
    
    # Выбор стратегии
    print("Выберите стратегию для тестирования:")
    print("1. 📈 EMA + ML")
    print("2. ⚡ Price Action")
    print("3. 🎯 MACD + RSI")
    print("4. 📊 Bollinger Bands")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    strategies = {
        '1': EmaMlStrategy(),
        '2': PriceActionStrategy(),
        '3': MacdRsiStrategy(),
        '4': BollingerStrategy()
    }
    
    if choice not in strategies:
        print("❌ Неверный выбор")
        return
    
    strategy = strategies[choice]
    
    # Показываем текущие настройки стратегии
    print()
    print("=" * 60)
    print("⚙️ ТЕКУЩИЕ НАСТРОЙКИ СТРАТЕГИИ")
    print("=" * 60)
    
    if hasattr(strategy, 'settings'):
        settings = strategy.settings
        print(f"📊 EMA Threshold: {settings.get('ema_threshold', 0.005) * 100:.2f}%")
        if 'take_profit_percent' in settings and settings.get('take_profit_usdt', 0) == 0:
            print(f"🎯 Take Profit: {settings.get('take_profit_percent', 2.0):.2f}%")
        elif settings.get('take_profit_usdt', 0) > 0:
            print(f"🎯 Take Profit: {settings.get('take_profit_usdt', 0):.4f} USDT")
        print(f"🛑 Stop Loss: {settings.get('stop_loss_percent', 1.5):.1f}%")
        if 'ml_confidence_buy' in settings:
            print(f"🤖 ML Confidence Buy: {settings.get('ml_confidence_buy', 0.4):.2f}")
            print(f"🤖 ML Confidence Sell: {settings.get('ml_confidence_sell', 0.3):.2f}")
    
    print("=" * 60)
    print()
    
    # Вопрос о сбросе настроек
    reset = input("Сбросить настройки стратегии к значениям по умолчанию? (y/n, по умолчанию n): ").strip().lower()
    if reset == 'y':
        if hasattr(strategy, 'reset_to_defaults'):
            strategy.reset_to_defaults()
            print("✅ Настройки сброшены к значениям по умолчанию")
        elif hasattr(strategy, 'default_settings'):
            strategy.settings = strategy.default_settings.copy()
            print("✅ Настройки сброшены к значениям по умолчанию")
        print()
    
    # Редактирование параметров стратегии
    edit_params = input("Редактировать параметры стратегии? (y/n, по умолчанию n): ").strip().lower()
    if edit_params == 'y' and hasattr(strategy, 'settings'):
        print()
        print("=" * 60)
        print("⚙️ РЕДАКТИРОВАНИЕ ПАРАМЕТРОВ СТРАТЕГИИ")
        print("=" * 60)
        
        settings = strategy.settings
        
        # EMA Threshold
        if 'ema_threshold' in settings:
            current_ema = settings['ema_threshold'] * 100
            ema_input = input(f"EMA Threshold (текущее: {current_ema:.2f}%, Enter для пропуска): ").strip()
            if ema_input.replace('.', '').isdigit():
                settings['ema_threshold'] = float(ema_input) / 100
                print(f"✅ EMA Threshold установлен: {float(ema_input):.2f}%")
        
        # Take Profit
        if 'take_profit_percent' in settings and settings.get('take_profit_usdt', 0) == 0:
            current_tp = settings['take_profit_percent']
            tp_input = input(f"Take Profit (текущее: {current_tp:.4f}%, Enter для пропуска): ").strip()
            if tp_input.replace('.', '').isdigit():
                settings['take_profit_percent'] = float(tp_input)
                settings['take_profit_usdt'] = 0.0  # Убеждаемся, что режим процентов
                print(f"✅ Take Profit установлен: {float(tp_input):.4f}%")
        elif settings.get('take_profit_usdt', 0) > 0:
            current_tp = settings['take_profit_usdt']
            tp_input = input(f"Take Profit USDT (текущее: {current_tp:.4f} USDT, Enter для пропуска): ").strip()
            if tp_input.replace('.', '').isdigit():
                settings['take_profit_usdt'] = float(tp_input)
                print(f"✅ Take Profit USDT установлен: {float(tp_input):.4f} USDT")
        
        # Stop Loss
        if 'stop_loss_percent' in settings:
            current_sl = settings['stop_loss_percent']
            sl_input = input(f"Stop Loss (текущее: {current_sl:.1f}%, Enter для пропуска): ").strip()
            if sl_input.replace('.', '').isdigit():
                settings['stop_loss_percent'] = float(sl_input)
                print(f"✅ Stop Loss установлен: {float(sl_input):.1f}%")
        
        # ML Confidence Buy
        if 'ml_confidence_buy' in settings:
            current_ml_buy = settings['ml_confidence_buy']
            ml_buy_input = input(f"ML Confidence Buy (текущее: {current_ml_buy:.2f}, Enter для пропуска): ").strip()
            if ml_buy_input.replace('.', '').isdigit():
                settings['ml_confidence_buy'] = float(ml_buy_input)
                print(f"✅ ML Confidence Buy установлен: {float(ml_buy_input):.2f}")
        
        # ML Confidence Sell
        if 'ml_confidence_sell' in settings:
            current_ml_sell = settings['ml_confidence_sell']
            ml_sell_input = input(f"ML Confidence Sell (текущее: {current_ml_sell:.2f}, Enter для пропуска): ").strip()
            if ml_sell_input.replace('.', '').isdigit():
                settings['ml_confidence_sell'] = float(ml_sell_input)
                print(f"✅ ML Confidence Sell установлен: {float(ml_sell_input):.2f}")
        
        print("=" * 60)
        print()
    
    # Параметры тестирования
    symbol = input("Введите торговую пару (по умолчанию BTC/USDT): ").strip() or "BTC/USDT"
    timeframe = input("Введите таймфрейм (1h, 4h, 1d, по умолчанию 1h): ").strip() or "1h"
    days = input("Введите количество дней для тестирования (по умолчанию 30): ").strip()
    days = int(days) if days.isdigit() else 30
    
    initial_balance = input("Введите начальный баланс в USDT (по умолчанию 1000): ").strip()
    initial_balance = float(initial_balance) if initial_balance.replace('.', '').isdigit() else 1000.0
    
    # Размер ставки
    size_percent_input = input("Введите размер ставки в % от баланса (по умолчанию 10%): ").strip()
    size_percent = float(size_percent_input) / 100 if size_percent_input.replace('.', '').isdigit() else 0.1
    
    print()
    print("=" * 60)
    print("🚀 Запуск бэктестинга...")
    print("=" * 60)
    print()
    
    # Создание движка и запуск теста
    engine = BacktestEngine(initial_balance=initial_balance, size_percent=size_percent)
    stats = engine.run_backtest(strategy, symbol, timeframe, days)
    
    if stats:
        print()
        print("✅ Бэктестинг завершен успешно!")
        print()
        
        # Сохранение результатов
        save = input("Сохранить результаты в файл? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"backtest_{strategy.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("РЕЗУЛЬТАТЫ БЭКТЕСТИНГА\n")
                f.write("=" * 60 + "\n")
                f.write(f"Стратегия: {strategy.name}\n")
                f.write(f"Пара: {symbol}\n")
                f.write(f"Таймфрейм: {timeframe}\n")
                f.write(f"Период: {days} дней\n")
                f.write(f"Начальный баланс: {initial_balance:.2f} USDT\n")
                f.write(f"Конечный баланс: {stats['total_profit'] + initial_balance:.2f} USDT\n")
                f.write(f"Прибыль: {stats['total_profit']:.2f} USDT ({stats['total_profit_percent']:.2f}%)\n")
                f.write(f"Всего сделок: {stats['total_trades']}\n")
                f.write(f"Win Rate: {stats['win_rate']:.1f}%\n")
                f.write(f"Profit Factor: {stats['profit_factor']:.2f}\n")
                f.write(f"Максимальная просадка: {stats['max_drawdown']:.2f}%\n")
            print(f"✅ Результаты сохранены в {filename}")


if __name__ == "__main__":
    main()

