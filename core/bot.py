"""
ОСНОВНОЙ КЛАСС БОТА
"""
import threading
import time
from datetime import datetime
from config.settings import SettingsManager
from core.exchange import ExchangeManager
from core.risk_manager import RiskManager
from analytics.metrics import AnalyticsMetrics
from ml.model import MLModel
from telegram.bot import TelegramBot
from strategies.ema_ml import EmaMlStrategy
from strategies.price_action import PriceActionStrategy
from strategies.macd_rsi import MacdRsiStrategy
from strategies.bollinger import BollingerStrategy
from utils.logger import log_info, log_error
import json
import os

class AdvancedTradingBot:
    def __init__(self):
        """Оптимизированная инициализация бота"""
        # БЫСТРАЯ инициализация основных компонентов
        self.settings = SettingsManager()
        self.exchange = ExchangeManager() 
        self.risk_manager = RiskManager(self.settings.risk_settings)
        self.metrics = AnalyticsMetrics()
        # Состояние бота
        self.position = None
        self.entry_price = 0
        self.last_signal = None
        self.last_price = None
        self.is_running = True
        # Размер текущей позиции в USDT (фиксируется при открытии)
        self.current_position_size_usdt = 0
        # Время последней сделки (для защиты от частых сделок)
        self.last_trade_time = 0
        # Сразу запускаем Telegram для мгновенного отклика
        self.telegram = TelegramBot(self)
        # Стратегии (быстрая инициализация)
        self.strategies = {
            'ema_ml': EmaMlStrategy(),
            'price_action': PriceActionStrategy(), 
            'macd_rsi': MacdRsiStrategy(),
            'bollinger': BollingerStrategy()
        }
        log_info("⚡ Бот быстро инициализирован, ML загружается в фоне...")
        # ML в фоне - не блокирует старт
        self.ml_model = MLModel()
        self.start_background_ml()

        # 🟢 ЗАГРУЖАЕМ СОСТОЯНИЕ ПОЗИЦИИ ИЗ ФАЙЛА
        self.load_position_state()

    def start_background_ml(self):
        """Фоновая загрузка ML"""
        def ml_worker():
            if self.settings.ml_settings['enabled']:
                if not self.ml_model.load_model():
                    log_info("🤖 Фоновое обучение ML...")
                    # Используем легкий режим обучения
                    self.ml_model.train(self.exchange.exchange, limit=80)
                else:
                    log_info("✅ ML модель загружена из кэша")
            else:
                log_info("🤖 ML отключен в настройках")
        threading.Thread(target=ml_worker, daemon=True).start()

    def get_active_strategy(self):
        """Получение активной стратегии с актуальными настройками"""
        strategy_name = self.settings.strategy_settings['active_strategy']
        strategy = self.strategies.get(strategy_name, self.strategies['ema_ml'])
        # 🔧 ОБНОВЛЯЕМ НАСТРОЙКИ СТРАТЕГИИ ИЗ МЕНЕДЖЕРА НАСТРОЕК
        if strategy_name == 'ema_ml':
            strategy.settings.update({
                'ema_threshold': self.settings.settings.get('ema_cross_threshold', 0.005),
                'ml_confidence_buy': self.settings.ml_settings.get('confidence_threshold_buy', 0.4),
                'ml_confidence_sell': self.settings.ml_settings.get('confidence_threshold_sell', 0.3)
            })
        return strategy

    def execute_trading_cycle(self):
        """Выполнение одного цикла торговли"""
        try:
            # 🔧 ПРОВЕРКА: разрешена ли торговля
            if not self.settings.settings.get('trading_enabled', True):
                log_info("⏸️ Торговля отключена в настройках")
                return
            # 🔧 ПРОВЕРКА: достаточно ли средств
            balance = self.exchange.get_balance()
            if not balance or balance['free_usdt'] < 0.1:  # Минимум 0.1 USDT
                log_info("❌ Недостаточно средств для торговли (минимум 0.1 USDT)")
                return
            # Получаем рыночные данные
            symbol = self.settings.trading_pairs['active_pair']
            market_data = self.exchange.get_market_data(symbol)
            if not market_data:
                log_info("❌ Не удалось получить рыночные данные")
                return
            # Получаем ML предсказание (если модель готова)
            ml_confidence, ml_signal = 0.5, "⚪ ML ЗАГРУЗКА"
            if self.ml_model.is_trained:
                ml_confidence, ml_signal = self.ml_model.predict(market_data.get('ohlcv', []))
            # Получаем сигнал от активной стратегии
            strategy = self.get_active_strategy()
            # 💰 РАСЧЕТ РАЗМЕРА ПОЗИЦИИ С УЧЕТОМ МИНИМАЛЬНОГО ОБЪЕМА
            trade_amount_percent = self.settings.settings['trade_amount_percent']
            initial_position_size_usdt = balance['free_usdt'] * trade_amount_percent
            # 🔧 РАСЧЕТ МИНИМАЛЬНОГО РАЗМЕРА СТАВКИ ДЛЯ ДАННОЙ ПАРЫ
            min_amount = self.get_min_amount(symbol)
            min_position_usdt = min_amount * market_data['current_price']
            log_info(f"💰 МИНИМАЛЬНЫЕ ТРЕБОВАНИЯ: {min_amount:.6f} {symbol.split('/')[0]} = {min_position_usdt:.2f} USDT")
            log_info(f"💰 РАСЧЕТНАЯ СТАВКА: {initial_position_size_usdt:.2f} USDT ({trade_amount_percent*100:.1f}% от баланса)")
            # 🔧 ЕСЛИ РАСЧЕТНЫЙ РАЗМЕР МЕНЬШЕ МИНИМАЛЬНОГО - ИСПОЛЬЗУЕМ МИНИМАЛЬНЫЙ
            position_size_usdt = initial_position_size_usdt
            if initial_position_size_usdt < min_position_usdt:
                if balance['free_usdt'] >= min_position_usdt:
                    position_size_usdt = min_position_usdt
                    log_info(f"💰 Увеличиваем ставку до минимальной: {position_size_usdt:.2f} USDT")
                else:
                    log_info(f"❌ Недостаточно средств для минимальной ставки. Нужно: {min_position_usdt:.2f} USDT, есть: {balance['free_usdt']:.2f} USDT")
                    return
            # 🔧 ПРОВЕРКА МИНИМАЛЬНОГО ОБЪЕМА KUCOIN (0.1 USDT)
            if position_size_usdt < 0.1:
                log_info(f"⚠️ Размер ставки {position_size_usdt:.2f} USDT меньше минимального 0.1 USDT KuCoin")
                return
            signal = strategy.calculate_signal(
                market_data, 
                ml_confidence, 
                ml_signal,
                position_size_usdt=position_size_usdt
            )
            # 🔍 ДИАГНОСТИЧЕСКОЕ ЛОГИРОВАНИЕ
            log_info("🔍 === ДИАГНОСТИКА ТОРГОВОГО ЦИКЛА ===")
            log_info(f"📊 РЫНОЧНЫЕ ДАННЫЕ: цена={market_data['current_price']:.2f}, EMA_diff={market_data.get('ema_diff_percent', 0):.4f}")
            log_info(f"🤖 ML ДАННЫЕ: confidence={ml_confidence:.3f}, signal='{ml_signal}'")
            log_info(f"💰 БАЛАНС: свободно={balance['free_usdt']:.2f} USDT, ставка={position_size_usdt:.2f} USDT")
            log_info(f"🤖 ПОЗИЦИЯ: {self.position}, last_signal='{self.last_signal}'")
            if hasattr(strategy, 'settings'):
                ema_threshold = strategy.settings.get('ema_threshold', 0.005)
                ml_buy_threshold = strategy.settings.get('ml_confidence_buy', 0.4)
                log_info(f"⚙️ ПАРАМЕТРЫ СТРАТЕГИИ: EMA_threshold={ema_threshold:.4f}, ML_buy_threshold={ml_buy_threshold:.2f}")
            # Проверяем риски
            risk_ok, risk_message = self.risk_manager.check_trade_risk(
                signal, 
                market_data['current_price'],
                (position_size_usdt / balance['free_usdt']) * 100 if balance['free_usdt'] > 0 else 0,
                market_data
            )
            log_info(f"⚡ ПРОВЕРКА РИСКОВ: risk_ok={risk_ok}, message='{risk_message}'")
            # 🔧 ИСПРАВЛЕННАЯ ЛОГИКА ПРОВЕРКИ СИГНАЛОВ
            should_execute = False
            execution_reason = ""
            if risk_ok and signal != 'wait':
                # 🔧 ЗАЩИТА ОТ ЧАСТЫХ СДЕЛОК (минимум 60 секунд между сделками)
                current_time = time.time()
                time_since_last_trade = current_time - self.last_trade_time
                min_trade_interval = 60  # 60 секунд
                if time_since_last_trade < min_trade_interval:
                    log_info(f"⏰ Слишком рано для новой сделки: {time_since_last_trade:.0f} сек < {min_trade_interval} сек")
                    should_execute = False
                    execution_reason = "Слишком частые сделки"
                elif signal == 'buy' and self.position != 'long':
                    # Сигнал на покупку и позиция не открыта
                    should_execute = True
                    execution_reason = "Открытие LONG позиции"
                    log_info(f"🚀 УСЛОВИЯ ПОКУПКИ ВЫПОЛНЕНЫ: signal='{signal}', position='{self.position}'")
                elif signal == 'sell' and self.position == 'long':
                    # Сигнал на продажу и позиция открыта
                    should_execute = True
                    execution_reason = "Закрытие LONG позиции"
                    log_info(f"🚀 УСЛОВИЯ ПРОДАЖИ ВЫПОЛНЕНЫ: signal='{signal}', position='{self.position}'")
                else:
                    execution_reason = f"Несовпадение сигнала и позиции (signal: {signal}, position: {self.position})"
                    log_info(f"🔍 СИГНАЛ ПРОПУЩЕН: {execution_reason}")
            else:
                execution_reason = f"Риски не пройдены или сигнал 'wait' (risk_ok: {risk_ok}, signal: {signal})"
            # Исполняем сделку если все проверки пройдены
            if should_execute:
                log_info(f"🚀 ВЫПОЛНЯЕМ СДЕЛКУ: {signal} - {execution_reason}")
                self.execute_trade(signal, market_data, ml_confidence, ml_signal, position_size_usdt)
                # 🔧 ОБНОВЛЯЕМ LAST_SIGNAL И ВРЕМЯ СДЕЛКИ ТОЛЬКО ПРИ ВЫПОЛНЕНИИ СДЕЛКИ
                self.last_signal = signal
                self.last_trade_time = time.time()
            else:
                log_info(f"🔍 СДЕЛКА НЕ ВЫПОЛНЕНА: {execution_reason}")
            # Отправляем обновление рынка
            self.telegram.send_market_update(market_data, signal, ml_confidence, ml_signal)
        except Exception as e:
            log_error(f"❌ Ошибка в торговом цикле: {e}")

    def execute_trade(self, signal, market_data, ml_confidence, ml_signal, position_size_usdt):
        """Исполнение сделки с информацией о размере позиции"""
        try:
            strategy = self.get_active_strategy()
            symbol = self.settings.trading_pairs['active_pair']
            current_price = market_data['current_price']
            if signal == 'buy' and self.position != 'long':
                # Логика покупки
                self.position = 'long'
                # ❗ ФИКСИРУЕМ РАЗМЕР ПОЗИЦИИ В USDT
                self.current_position_size_usdt = position_size_usdt
                if not self.settings.settings['demo_mode']:
                    # Реальная торговля
                    amount = position_size_usdt / current_price  # Расчет количества монет
                    order, message = self.exchange.create_order(
                        symbol, 'market', 'buy', amount
                    )
                    if not order:
                        log_info(f"❌ Ошибка создания ордера: {message}")
                        return
                    log_info(f"✅ Реальный ордер создан: {order['id']}")
                    # В реальной торговле используем цену исполнения ордера
                    executed_price = current_price
                else:
                    # Демо-режим
                    order = {'id': 'demo_buy', 'status': 'closed'}
                    message = f"ДЕМО-РЕЖИМ | Размер ставки: {position_size_usdt:.2f} USDT"
                    executed_price = current_price
                    log_info("✅ Демо-покупка выполнена")
                # Обновляем информацию о позиции в стратегии
                strategy.update_position_info(signal, executed_price)
                # Обновляем метрики
                trade_result = {
                    'symbol': symbol,
                    'signal': 'buy',
                    'price': executed_price,
                    'profit': 0,
                    'profit_percent': 0,
                    'position_size': trade_amount_percent * 100,
                    'position_size_usdt': position_size_usdt
                }
                self.metrics.update_metrics(trade_result)
                self.risk_manager.update_after_trade(trade_result)
                # Сохраняем состояние позиции в файл
                self.save_position_state()
                # Отправляем уведомление
                self.telegram.send_trade_signal(
                    signal, market_data, ml_confidence, ml_signal, 
                    strategy.name, message, position_size_usdt
                )
            elif signal == 'sell' and self.position == 'long':
                # Логика продажи
                profit_percent = 0
                profit_usdt = 0
                if not self.settings.settings['demo_mode']:
                    # Реальная торговля
                    amount = position_size_usdt / strategy.entry_price  # Количество купленных монет
                    order, message = self.exchange.create_order(
                        symbol, 'market', 'sell', amount
                    )
                    if not order:
                        log_info(f"❌ Ошибка создания ордера продажи: {message}")
                        return
                    log_info(f"✅ Реальный ордер продажи создан: {order['id']}")
                    executed_price = current_price
                else:
                    # Демо-режим
                    order = {'id': 'demo_sell', 'status': 'closed'}
                    message = f"ДЕМО-РЕЖИМ | Прибыль: {profit_usdt:+.2f} USDT"
                    executed_price = current_price
                    log_info("✅ Демо-продажа выполнена")
                # Расчет прибыли используем из стратегии
                if strategy.entry_price > 0:
                    profit_percent = ((executed_price - strategy.entry_price) / strategy.entry_price) * 100
                    profit_usdt = self.current_position_size_usdt * (profit_percent / 100)
                # Обновляем информацию о позиции в стратегии
                strategy.update_position_info(signal, executed_price)
                # Обновляем метрики
                trade_result = {
                    'symbol': symbol,
                    'signal': 'sell',
                    'price': executed_price,
                    'profit': profit_percent,
                    'profit_percent': profit_percent,
                    'position_size': trade_amount_percent * 100,
                    'position_size_usdt': position_size_usdt,
                    'profit_usdt': profit_usdt
                }
                self.metrics.update_metrics(trade_result)
                self.risk_manager.update_after_trade(trade_result)
                # Сбрасываем позицию
                self.position = None
                self.current_position_size_usdt = 0
                self.entry_price = 0
                # Сохраняем состояние позиции в файл (позиция закрыта)
                self.save_position_state()
                # Отправляем уведомление
                self.telegram.send_trade_signal(
                    signal, market_data, ml_confidence, ml_signal,
                    strategy.name, message, position_size_usdt, profit_usdt
                )
        except Exception as e:
            log_error(f"❌ Ошибка исполнения сделки: {e}")

    def calculate_trade_amount(self):
        """Расчет размера сделки"""
        balance = self.exchange.get_balance()
        if balance and balance['free_usdt'] > 0:
            return balance['free_usdt'] * self.settings.settings['trade_amount_percent']
        return 0

    def run(self):
        """Основной цикл работы бота - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        log_info("🚀 ЗАПУСК ОСНОВНОГО ЦИКЛА БОТА")
        last_balance_check = time.time()
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                log_info(f"🔄 Цикл #{cycle_count} запущен")
                if self.settings.settings.get('trading_enabled', True):
                    log_info("🔍 Выполняем торговый цикл...")
                    self.execute_trading_cycle()
                    log_info("✅ Торговый цикл завершен")
                else:
                    log_info("⏸️ Торговля отключена в настройках")
                # Проверяем баланс каждые 5 минут
                current_time = time.time()
                if current_time - last_balance_check > 300:  # 5 минут
                    log_info("💰 Проверка баланса...")
                    self.telegram.send_balance_update()
                    last_balance_check = current_time
                log_info(f"💤 Пауза 30 секунд перед следующим циклом...")
                time.sleep(30)
            except KeyboardInterrupt:
                log_info("🛑 Бот остановлен пользователем (Ctrl+C)")
                self.stop()
                break
            except Exception as e:
                log_error(f"❌ Ошибка в основном цикле: {e}")
                log_info("💤 Пауза 60 секунд перед повторной попыткой...")
                time.sleep(60)
        log_info("🔚 Основной цикл бота завершен")

    def stop(self):
        """Остановка бота"""
        self.is_running = False
        log_info("🛑 Бот остановлен")

    # 📁 МЕТОДЫ СОХРАНЕНИЯ И ЗАГРУЗКИ СОСТОЯНИЯ ПОЗИЦИИ
    def save_position_state(self):
        """Сохраняет состояние позиции в файл"""
        state = {
            'position': self.position,
            'entry_price': self.entry_price,
            'position_size_usdt': self.current_position_size_usdt,
            'symbol': self.settings.trading_pairs['active_pair'],
            'opened_at': self.last_trade_time
        }
        with open('position_state.json', 'w') as f:
            json.dump(state, f, indent=2)
        log_info("💾 Состояние позиции сохранено в файл")

    def load_position_state(self):
        """Загружает состояние позиции из файла"""
        try:
            if os.path.exists('position_state.json'):
                with open('position_state.json', 'r') as f:
                    state = json.load(f)
                # Проверяем, что это та же торговая пара
                if state.get('symbol') == self.settings.trading_pairs['active_pair']:
                    self.position = state.get('position')
                    self.entry_price = state.get('entry_price', 0)
                    self.current_position_size_usdt = state.get('position_size_usdt', 0)
                    self.last_trade_time = state.get('opened_at', 0)
                    if self.position == 'long':
                        log_info(f"✅ Восстановлена открытая позиция: вход {self.entry_price:.2f} USDT, размер {self.current_position_size_usdt:.2f} USDT")
                else:
                    log_info("🔄 Торговая пара изменилась — игнорируем старое состояние позиции")
        except Exception as e:
            log_error(f"❌ Ошибка загрузки состояния позиции: {e}")

    def get_min_amount(self, symbol):
        """Получение минимального количества для торговой пары"""
        min_amounts = {
            'BTC/USDT': 0.00001,
            'ETH/USDT': 0.001,
            'SOL/USDT': 0.1,
            'ADA/USDT': 1.0,
            'DOT/USDT': 0.1,
            'LINK/USDT': 0.1
        }
        return min_amounts.get(symbol, 0.001)