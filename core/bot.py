"""
ОСНОВНОЙ КЛАСС БОТА
"""
import threading
import time
import json
import os
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
from utils.logger import log_info, log_error, log_separator, log_section, log_empty_line

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
        
        # 🔧 УСТАНАВЛИВАЕМ ССЫЛКУ НА БОТА В НАСТРОЙКАХ ДО ИНИЦИАЛИЗАЦИИ TELEGRAM
        self.settings.set_bot_reference(self)
        
        # Сразу запускаем Telegram для мгновенного отклика
        # 🔧 ИНИЦИАЛИЗИРУЕМ telegram ДАЖЕ ЕСЛИ ОШИБКА (чтобы избежать AttributeError)
        try:
            self.telegram = TelegramBot(self)
        except Exception as e:
            log_error(f"❌ Ошибка инициализации Telegram бота: {e}")
            self.telegram = None  # Устанавливаем None, чтобы избежать AttributeError
        # Стратегии (быстрая инициализация)
        self.strategies = {
            'ema_ml': EmaMlStrategy(),
            'price_action': PriceActionStrategy(), 
            'macd_rsi': MacdRsiStrategy(),
            'bollinger': BollingerStrategy()
        }
        
        # 🔧 ЗАГРУЖАЕМ НАСТРОЙКИ СТРАТЕГИЙ ПОСЛЕ ИХ СОЗДАНИЯ
        self.settings.load_strategy_settings()

        # 🔴 ТОРГОВЛЯ ВСЕГДА ОТКЛЮЧЕНА ПРИ ЗАПУСКЕ (даже если была включена ранее)
        self.settings.settings['trading_enabled'] = False
        self.settings.save_settings()
        log_info("⚠️ Торговля отключена при запуске (требуется ручное включение).")

        log_info("⚡ Бот быстро инициализирован, ML загружается в фоне...")
        # ML в фоне - не блокирует старт
        self.ml_model = MLModel()
        self.start_background_ml()
        # 🟢 ЛЕНИВАЯ ЗАГРУЗКА ПОЗИЦИИ - не блокирует старт WebApp
        self._position_loaded = False
        threading.Thread(target=self._load_position_background, daemon=True).start()

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
            # Загружаем EMA настройки из сохраненных значений
            ema_threshold = self.settings.ml_settings.get('last_ema_threshold', 0.0025)
            # Если есть старое значение ema_cross_threshold, используем его для обратной совместимости
            if ema_threshold == 0.0025 and 'ema_cross_threshold' in self.settings.settings:
                ema_threshold = self.settings.settings.get('ema_cross_threshold', 0.0025)
            
            strategy.settings.update({
                'ema_threshold': ema_threshold,
                'ema_fast_period': self.settings.ml_settings.get('last_ema_fast_period', 9),
                'ema_slow_period': self.settings.ml_settings.get('last_ema_slow_period', 21),
                'ml_confidence_buy': self.settings.ml_settings.get('confidence_threshold_buy', 0.4),
                'ml_confidence_sell': self.settings.ml_settings.get('confidence_threshold_sell', 0.3)
            })
        return strategy

    def execute_trading_cycle(self):
        """Выполнение одного цикла торговли"""
        try:
            log_empty_line()
            log_separator("-", 80)
            
            # Получаем рыночные данные для обновления (даже если торговля отключена)
            symbol = self.settings.trading_pairs['active_pair']
            # Получаем стратегию для настройки EMA периодов
            strategy = self.get_active_strategy()
            ema_fast = strategy.settings.get('ema_fast_period', 9)
            ema_slow = strategy.settings.get('ema_slow_period', 21)
            market_data = self.exchange.get_market_data(symbol, ema_fast_period=ema_fast, ema_slow_period=ema_slow)
            if not market_data:
                log_info("❌ Не удалось получить рыночные данные")
                log_separator("-", 80)
                return
            
            # Получаем ML предсказание (если модель готова)
            ml_confidence, ml_signal = 0.5, "⚪ ML ЗАГРУЗКА"
            if self.ml_model.is_trained:
                ml_confidence, ml_signal = self.ml_model.predict(market_data.get('ohlcv', []))
            signal = strategy.calculate_signal(
                market_data, 
                ml_confidence, 
                ml_signal,
                position_size_usdt=0  # Не важно для сигнала
            )
            
            # 🔧 ОТПРАВЛЯЕМ ОБНОВЛЕНИЕ РЫНКА ДАЖЕ ЕСЛИ ТОРГОВЛЯ ОТКЛЮЧЕНА
            # Это нужно для отображения информации о позиции и рынке
            self.telegram.send_market_update(market_data, signal, ml_confidence, ml_signal)
            
            # 🔧 ПРОВЕРКА: разрешена ли торговля
            if not self.settings.settings.get('trading_enabled', False):
                log_info("⏸️ Торговля отключена в настройках")
                log_separator("-", 80)
                return
            # 🔧 ПРОВЕРКА: достаточно ли средств
            balance = self.exchange.get_balance()
            if not balance or balance['free_usdt'] < 0.1:  # Минимум 0.1 USDT
                log_info("❌ Недостаточно средств для торговли (минимум 0.1 USDT)")
                log_separator("-", 80)
                return
            # Рыночные данные и ML уже получены выше
            # strategy уже получена выше
            # 💰 РАСЧЕТ РАЗМЕРА ПОЗИЦИИ С УЧЕТОМ МИНИМАЛЬНОГО ОБЪЕМА
            log_section("РАСЧЕТ РАЗМЕРА СТАВКИ", "-", 80)
            trade_amount_percent = self.settings.settings['trade_amount_percent']
            initial_position_size_usdt = balance['free_usdt'] * trade_amount_percent
            # 🔧 РАСЧЕТ МИНИМАЛЬНОГО РАЗМЕРА СТАВКИ ДЛЯ ДАННОЙ ПАРЫ (биржевые лимиты)
            min_amount, min_cost = self.exchange.get_min_limits(symbol)
            min_position_usdt_from_amount = float(min_amount) * market_data['current_price']
            # Минимальная сумма в USDT берется из биржи (fallback 0.1)
            min_position_usdt = max(min_position_usdt_from_amount, float(min_cost))
            log_info(f"💰 МИНИМУМ ПО КОЛИЧЕСТВУ: {min_amount:.6f} {symbol.split('/')[0]} = {min_position_usdt_from_amount:.4f} USDT")
            log_info(f"💰 МИНИМУМ ПО СУММЕ (биржа): {float(min_cost):.4f} USDT")
            log_info(f"💰 ИТОГОВЫЙ МИНИМУМ: {min_position_usdt:.4f} USDT")
            log_info(f"💰 РАСЧЕТНАЯ СТАВКА (от процента): {initial_position_size_usdt:.4f} USDT ({trade_amount_percent*100:.1f}% от баланса)")
            # 🔧 ЕСЛИ РАСЧЕТНЫЙ РАЗМЕР МЕНЬШЕ МИНИМАЛЬНОГО - ИСПОЛЬЗУЕМ МИНИМАЛЬНЫЙ
            position_size_usdt = initial_position_size_usdt
            if initial_position_size_usdt < min_position_usdt:
                if balance['free_usdt'] >= min_position_usdt:
                    position_size_usdt = min_position_usdt
                    log_info(f"💰 Увеличиваем ставку до минимальной: {position_size_usdt:.4f} USDT")
                else:
                    log_info(f"❌ Недостаточно средств для минимальной ставки. Нужно: {min_position_usdt:.4f} USDT, есть: {balance['free_usdt']:.2f} USDT")
                    log_separator("-", 80)
                    return
            # 🔧 ВЫВОД ИТОГОВОЙ СТАВКИ (после всех проверок)
            if position_size_usdt != initial_position_size_usdt:
                log_info(f"💰 ИТОГОВАЯ СТАВКА: {position_size_usdt:.4f} USDT (увеличена до минимума)")
            else:
                log_info(f"💰 ИТОГОВАЯ СТАВКА: {position_size_usdt:.4f} USDT")
            signal = strategy.calculate_signal(
                market_data, 
                ml_confidence, 
                ml_signal,
                position_size_usdt=position_size_usdt
            )
            # 🔍 ДИАГНОСТИЧЕСКОЕ ЛОГИРОВАНИЕ
            log_empty_line()
            log_section("ДИАГНОСТИКА ТОРГОВОГО ЦИКЛА", "=", 80)
            log_info(f"📊 РЫНОЧНЫЕ ДАННЫЕ: цена={market_data['current_price']:.2f}, EMA_diff={market_data.get('ema_diff_percent', 0):.4f}")
            log_info(f"🤖 ML ДАННЫЕ: confidence={ml_confidence:.3f}, signal='{ml_signal}'")
            log_info(f"💰 БАЛАНС: свободно={balance['free_usdt']:.2f} USDT, ставка={position_size_usdt:.2f} USDT")
            log_info(f"🤖 ПОЗИЦИЯ: {self.position}, last_signal='{self.last_signal}'")
            if hasattr(strategy, 'settings'):
                ema_threshold = strategy.settings.get('ema_threshold', 0.005)
                ml_buy_threshold = strategy.settings.get('ml_confidence_buy', 0.4)
                log_info(f"⚙️ ПАРАМЕТРЫ СТРАТЕГИИ: EMA_threshold={ema_threshold:.4f}, ML_buy_threshold={ml_buy_threshold:.2f}")
            log_empty_line()
            # Проверяем риски
            risk_ok, risk_message = self.risk_manager.check_trade_risk(
                signal, 
                market_data['current_price'],
                (position_size_usdt / balance['free_usdt']) * 100 if balance['free_usdt'] > 0 else 0,
                market_data
            )
            log_info(f"⚡ ПРОВЕРКА РИСКОВ: risk_ok={risk_ok}, message='{risk_message}'")
            log_empty_line()
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
                    # 🔧 ИСПРАВЛЕНИЕ: Если сигнал 'buy', а position уже 'long', это ошибка состояния
                    # Возможно, позиция была восстановлена из файла, но на бирже её нет
                    if signal == 'buy' and self.position == 'long':
                        log_info("⚠️ Обнаружено несоответствие: сигнал 'buy', но position='long'. Проверяем состояние...")
                        # Проверяем открытые ордера на бирже
                        open_orders = self.exchange.get_open_orders(symbol)
                        if len(open_orders) == 0:
                            # На бирже нет открытых ордеров - сбрасываем состояние
                            log_info("⚠️ На бирже нет открытых позиций. Сбрасываем внутреннее состояние.")
                            self.position = None
                            self.current_position_size_usdt = 0
                            self.entry_price = 0
                            strategy = self.get_active_strategy()
                            strategy.position = None
                            strategy.position_size_usdt = 0
                            self.save_position_state()
            else:
                execution_reason = f"Риски не пройдены или сигнал 'wait' (risk_ok: {risk_ok}, signal: {signal})"
            # Исполняем сделку если все проверки пройдены
            log_section("РЕШЕНИЕ О СДЕЛКЕ", "-", 80)
            if should_execute:
                log_info(f"🚀 ВЫПОЛНЯЕМ СДЕЛКУ: {signal} - {execution_reason}")
                self.execute_trade(signal, market_data, ml_confidence, ml_signal, position_size_usdt)
                # 🔧 ОБНОВЛЯЕМ LAST_SIGNAL И ВРЕМЯ СДЕЛКИ ТОЛЬКО ПРИ ВЫПОЛНЕНИИ СДЕЛКИ
                self.last_signal = signal
                self.last_trade_time = time.time()
            else:
                log_info(f"🔍 СДЕЛКА НЕ ВЫПОЛНЕНА: {execution_reason}")
            log_empty_line()
            # Обновление рынка уже отправлено выше (до проверки торговли)
            log_separator("-", 80)
        except Exception as e:
            log_error(f"❌ Ошибка в торговом цикле: {e}")

    def execute_trade(self, signal, market_data, ml_confidence, ml_signal, position_size_usdt):
        """Исполнение сделки с информацией о размере позиции"""
        try:
            log_empty_line()
            log_section(f"ИСПОЛНЕНИЕ СДЕЛКИ: {signal.upper()}", "=", 80)
            strategy = self.get_active_strategy()
            symbol = self.settings.trading_pairs['active_pair']
            current_price = market_data['current_price']
            
            # ⚠️ КРИТИЧЕСКАЯ ПРОВЕРКА В ПЕРВУЮ ОЧЕРЕДЬ: блокируем покупки если есть открытые позиции
            if signal == 'buy':
                from utils.position_manager import get_positions_count
                existing_positions_count = get_positions_count(symbol)
                
                if existing_positions_count > 0:
                    log_info(f"⛔ ПОКУПКА ОТМЕНЕНА: Уже есть {existing_positions_count} открытых позиций для {symbol}")
                    log_info(f"   📋 Политика: не открываем новые позиции при наличии открытых")
                    return
                
                log_info(f"✅ Проверка пройдена: открытых позиций нет, можно покупать")
            
            if signal == 'buy' and self.position != 'long':
                
                # Логика покупки
                # 🔧 ИСПРАВЛЕНИЕ: НЕ устанавливаем position до успешного создания ордера
                
                # 🔧 ПРОВЕРЯЕМ РЕАЛЬНОЕ СОСТОЯНИЕ ПОЗИЦИИ НА БИРЖЕ (для случая, если позиция уже есть)
                # Получаем все открытые покупки (покупки после последней продажи)
                existing_buy_trades = []
                max_existing_price = 0.0
                existing_position_size = 0
                if not self.settings.settings['demo_mode']:
                    existing_buy_trades, max_existing_price = self.exchange.get_open_buy_trades_after_last_sell(symbol)
                    if existing_buy_trades:
                        log_info(f"🔍 Обнаружены открытые покупки после последней продажи: {len(existing_buy_trades)} покупок")
                        log_info(f"   • Максимальная цена среди открытых покупок: {max_existing_price:.2f} USDT")
                        # Получаем размер существующей позиции
                        position_info = self.exchange.check_open_position(symbol)
                        existing_position_size = position_info.get('position_size_usdt', 0)
                
                if not self.settings.settings['demo_mode']:
                    # Реальная торговля
                    amount = position_size_usdt / current_price  # Расчет количества монет
                    order, message = self.exchange.create_order(
                        symbol, 'market', 'buy', amount
                    )
                    if not order:
                        log_info(f"❌ Ошибка создания ордера: {message}")
                        # 🔧 Сбрасываем position, если он был установлен ошибочно
                        if self.position == 'long':
                            self.position = None
                            self.current_position_size_usdt = 0
                            self.save_position_state()
                        return
                    log_info(f"✅ Реальный ордер создан: {order['id']}")
                    # 🔧 В реальной торговле получаем ЦЕНУ ИСПОЛНЕНИЯ из ответа биржи
                    # CCXT может вернуть: 'average' (средняя цена), или можно рассчитать как cost/filled
                    executed_price = None
                    if 'average' in order and order['average']:
                        executed_price = order['average']
                        log_info(f"   📊 Цена исполнения из ордера (average): {executed_price:.2f} USDT")
                    elif 'cost' in order and 'filled' in order and order['filled'] > 0:
                        executed_price = order['cost'] / order['filled']
                        log_info(f"   📊 Цена исполнения рассчитана (cost/filled): {executed_price:.2f} USDT")
                    
                    # Если цена не найдена в ответе, пытаемся получить детальную информацию об ордере
                    if not executed_price:
                        try:
                            order_details = self.exchange.get_order_status(order['id'], symbol)
                            if order_details:
                                if 'average' in order_details and order_details['average']:
                                    executed_price = order_details['average']
                                    log_info(f"   📊 Цена исполнения из деталей ордера (average): {executed_price:.2f} USDT")
                                elif 'cost' in order_details and 'filled' in order_details and order_details['filled'] > 0:
                                    executed_price = order_details['cost'] / order_details['filled']
                                    log_info(f"   📊 Цена исполнения из деталей ордера (cost/filled): {executed_price:.2f} USDT")
                        except Exception as e:
                            log_error(f"   ⚠️ Ошибка получения деталей ордера: {e}")
                    
                    # Если всё ещё нет цены, используем текущую цену как fallback
                    if not executed_price:
                        executed_price = current_price
                        log_info(f"   ⚠️ Цена исполнения не найдена, используем текущую цену: {executed_price:.2f} USDT")
                    
                    # 🔧 КРИТИЧНО: Если есть открытые покупки (после последней продажи), берем МАКСИМАЛЬНУЮ цену
                    # среди всех открытых покупок включая новую покупку
                    # Это гарантирует, что при закрытии позиции будет прибыль относительно всех открытых покупок
                    if max_existing_price > 0:
                        final_entry_price = max(max_existing_price, executed_price)
                        log_info(f"   🔼 Максимальная цена среди открытых покупок: {max_existing_price:.2f} USDT")
                        log_info(f"   🔼 Новая покупка: {executed_price:.2f} USDT")
                        log_info(f"   ✅ Используем МАКСИМАЛЬНУЮ цену входа (из всех открытых покупок): {final_entry_price:.2f} USDT")
                        executed_price = final_entry_price
                        # Обновляем размер позиции (суммируем с существующей)
                        position_size_usdt = existing_position_size + position_size_usdt
                        log_info(f"   📊 Общий размер позиции: {position_size_usdt:.2f} USDT")
                    elif existing_buy_trades:
                        # Если есть покупки, но не удалось получить максимальную цену - используем текущую максимальную
                        prices = [t.get('price', 0) for t in existing_buy_trades if t.get('price', 0) > 0]
                        if prices:
                            max_price = max(prices)
                            final_entry_price = max(max_price, executed_price)
                            log_info(f"   🔼 Максимальная цена из открытых покупок: {max_price:.2f} USDT")
                            log_info(f"   🔼 Новая покупка: {executed_price:.2f} USDT")
                            log_info(f"   ✅ Используем МАКСИМАЛЬНУЮ цену входа: {final_entry_price:.2f} USDT")
                            executed_price = final_entry_price
                            # 🔧 Размер позиции остается фиксированным (размер одной ставки)
                            log_info(f"   📊 Размер позиции остается фиксированным (размер ставки): {position_size_usdt:.2f} USDT")
                    
                    # 🔧 ТОЛЬКО ПОСЛЕ УСПЕШНОГО СОЗДАНИЯ ОРДЕРА устанавливаем position
                    self.position = 'long'
                    self.current_position_size_usdt = position_size_usdt
                else:
                    # Демо-режим
                    order = {'id': 'demo_buy', 'status': 'closed'}
                    message = f"ДЕМО-РЕЖИМ | Размер ставки: {position_size_usdt:.2f} USDT"
                    executed_price = current_price
                    log_info("✅ Демо-покупка выполнена")
                    # 🔧 В демо-режиме тоже устанавливаем position только после успешной симуляции
                    self.position = 'long'
                    self.current_position_size_usdt = position_size_usdt
                    
                # 🔧 УСТАНАВЛИВАЕМ entry_price В БОТЕ (критично для сохранения состояния)
                # Цена входа берется из МАКСИМАЛЬНОЙ цены среди всех покупок (не средняя!)
                # Это гарантирует, что при закрытии позиции будет прибыль относительно всех покупок
                self.entry_price = executed_price
                self.last_trade_time = time.time()
                
                # Обновляем информацию о позиции в стратегии
                strategy.update_position_info(signal, executed_price)
                # 🔧 СОХРАНЯЕМ РАЗМЕР ПОЗИЦИИ В СТРАТЕГИИ
                strategy.position_size_usdt = position_size_usdt
                
                # Обновляем метрики
                trade_result = {
                    'symbol': symbol,
                    'signal': 'buy',
                    'price': executed_price,
                    'profit': 0,
                    'profit_percent': 0,
                    'position_size': self.settings.settings['trade_amount_percent'] * 100,
                    'position_size_usdt': position_size_usdt
                }
                self.metrics.update_metrics(trade_result)
                self.risk_manager.update_after_trade(trade_result)
                
                # 🔧 СОХРАНЯЕМ НАСТРОЙКИ ПОСЛЕ ИЗМЕНЕНИЯ
                self.settings.save_settings()
                
                # Сохраняем состояние позиции в файл
                self.save_position_state()
                # Отправляем уведомление
                self.telegram.send_trade_signal(
                    signal, market_data, ml_confidence, ml_signal, 
                    strategy.name, message, position_size_usdt
                )
                log_separator("=", 80)
                log_info("✅ СДЕЛКА ПОКУПКИ ЗАВЕРШЕНА")
                log_separator("=", 80)
            elif signal == 'sell' and self.position == 'long':
                # 🔧 ИСПРАВЛЕНИЕ: Расчет прибыли в правильном режиме
                profit_percent = 0
                profit_usdt = 0
                
                if hasattr(strategy, 'entry_price') and strategy.entry_price > 0:
                    # Расчет прибыли в зависимости от режима
                    take_profit_usdt_setting = strategy.settings.get('take_profit_usdt', 0.0)
                    
                    if take_profit_usdt_setting > 0:
                        # 🔹 РЕЖИМ USDT
                        profit_usdt = (current_price - strategy.entry_price) / strategy.entry_price * strategy.position_size_usdt
                        profit_percent = (profit_usdt / strategy.position_size_usdt) * 100
                        log_info(f"💰 Расчет прибыли (USDT режим): {profit_usdt:+.2f} USDT ({profit_percent:+.2f}%)")
                    else:
                        # 🔹 РЕЖИМ ПРОЦЕНТОВ
                        profit_percent = ((current_price - strategy.entry_price) / strategy.entry_price) * 100
                        profit_usdt = strategy.position_size_usdt * (profit_percent / 100)
                        log_info(f"💰 Расчет прибыли (% режим): {profit_percent:+.2f}% ({profit_usdt:+.2f} USDT)")
                
                if not self.settings.settings['demo_mode']:
                    # Реальная торговля
                    amount = strategy.position_size_usdt / strategy.entry_price  # Количество купленных монет
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
                    
                # Обновляем информацию о позиции в стратегии
                strategy.update_position_info(signal, executed_price)
                # Обновляем метрики
                trade_result = {
                    'symbol': symbol,
                    'signal': 'sell',
                    'price': executed_price,
                    'profit': profit_percent,
                    'profit_percent': profit_percent,
                    'position_size': self.settings.settings['trade_amount_percent'] * 100,
                    'position_size_usdt': strategy.position_size_usdt,
                    'profit_usdt': profit_usdt
                }
                self.metrics.update_metrics(trade_result)
                self.risk_manager.update_after_trade(trade_result)
                
                # 🔧 СОХРАНЯЕМ НАСТРОЙКИ ПОСЛЕ ИЗМЕНЕНИЯ
                self.settings.save_settings()
                
                # Сбрасываем позицию
                self.position = None
                self.current_position_size_usdt = 0
                self.entry_price = 0
                # 🔧 СБРАСЫВАЕМ ПОЗИЦИЮ В СТРАТЕГИИ
                strategy.position = None
                strategy.entry_price = 0
                strategy.position_size_usdt = 0
                # Сохраняем состояние позиции в файл (позиция закрыта)
                self.save_position_state()
                # Отправляем уведомление
                self.telegram.send_trade_signal(
                    signal, market_data, ml_confidence, ml_signal,
                    strategy.name, message, strategy.position_size_usdt, profit_usdt
                )
                log_separator("=", 80)
                log_info(f"✅ СДЕЛКА ПРОДАЖИ ЗАВЕРШЕНА | Прибыль: {profit_usdt:+.2f} USDT ({profit_percent:+.2f}%)")
                log_separator("=", 80)
        except Exception as e:
            log_error(f"❌ Ошибка исполнения сделки: {e}")
            log_separator("=", 80)

    def get_min_amount(self, symbol):
        """Получение минимального количества для торговой пары"""
        min_amounts = {
            'BTC/USDT': 0.00001,
            'ETH/USDT': 0.001,
            'SOL/USDT': 0.001,  # 🔧 ИСПРАВЛЕНО: минимум 0.001 SOL (не 0.1)
            'ADA/USDT': 1.0,
            'DOT/USDT': 0.1,
            'LINK/USDT': 0.1
        }
        return min_amounts.get(symbol, 0.001)

    def calculate_trade_amount(self):
        """Расчет размера сделки"""
        balance = self.exchange.get_balance()
        if balance and balance['free_usdt'] > 0:
            return balance['free_usdt'] * self.settings.settings['trade_amount_percent']
        return 0

    def run(self):
        """Основной цикл работы бота - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        log_empty_line()
        log_separator("=", 80)
        log_section("ЗАПУСК ОСНОВНОГО ЦИКЛА БОТА", "=", 80)
        log_separator("=", 80)
        log_empty_line()
        last_balance_check = time.time()
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                log_info(f"🔄 ЦИКЛ #{cycle_count}")
                if self.settings.settings.get('trading_enabled', False):
                    log_info("🔍 Выполняем торговый цикл...")
                    self.execute_trading_cycle()
                    log_info("✅ Торговый цикл завершен")
                else:
                    log_info("⏸️ Торговля отключена в настройках")
                # Проверяем баланс каждые 5 минут
                current_time = time.time()
                if current_time - last_balance_check > 300:  # 5 минут
                    log_empty_line()
                    log_separator("-", 80)
                    log_info("💰 Проверка баланса...")
                    # self.telegram.send_balance_update()  # Отключено: не выводить обновления баланса в чат
                    last_balance_check = current_time
                    log_separator("-", 80)
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
        # 🔧 СОХРАНЯЕМ НАСТРОЙКИ ПРИ ОСТАНОВКЕ
        self.settings.save_settings()
        log_info("🛑 Бот остановлен")

    # 📁 МЕТОДЫ СОХРАНЕНИЯ И ЗАГРУЗКИ СОСТОЯНИЯ ПОЗИЦИИ
    def save_position_state(self):
        """Сохраняет состояние позиции в файл (для текущей пары)"""
        strategy = self.get_active_strategy()
        # 🔧 ИСПОЛЬЗУЕМ entry_price ИЗ СТРАТЕГИИ, ЕСЛИ В БОТЕ ОН НУЛЕВОЙ (для обратной совместимости)
        entry_price_to_save = self.entry_price if self.entry_price > 0 else getattr(strategy, 'entry_price', 0)
        
        current_symbol = self.settings.trading_pairs['active_pair']
        
        # 🔧 ИЗМЕНЕНИЕ: Загружаем существующие позиции для всех пар
        all_positions = {}
        if os.path.exists('position_state.json'):
            try:
                with open('position_state.json', 'r') as f:
                    data = json.load(f)
                    # Если старый формат (одна позиция) - конвертируем
                    if 'symbol' in data and 'position' in data:
                        # Старый формат - сохраняем как позицию для этой пары
                        old_symbol = data.get('symbol', current_symbol)
                        all_positions[old_symbol] = {
                            'position': data.get('position'),
                            'entry_price': data.get('entry_price', 0),
                            'position_size_usdt': data.get('position_size_usdt', 0),
                            'opened_at': data.get('opened_at', 0),
                            'strategy_position_size_usdt': data.get('strategy_position_size_usdt', 0),
                            'strategy_entry_price': data.get('strategy_entry_price', 0)
                        }
                    elif isinstance(data, dict):
                        # Новый формат - словарь позиций по парам
                        all_positions = data
            except Exception as e:
                log_error(f"⚠️ Ошибка загрузки позиций: {e}")
                all_positions = {}
        
        # 🔧 НОВАЯ ЛОГИКА: Используем position_manager для работы с массивом позиций
        from utils.position_manager import load_position_state, add_position, close_all_positions
        
        if self.position == 'long':
            # Если позиция открывается - добавляем её через position_manager
            # НО! Не добавляем дубликаты - проверяем, была ли уже добавлена
            state = load_position_state('position_state.json')
            pair_data = state.get(current_symbol, {})
            existing_positions = pair_data.get('positions', [])
            
            # Проверяем, есть ли уже позиция с такой же ценой входа (избегаем дублирования)
            already_exists = any(
                abs(p.get('entry_price', 0) - entry_price_to_save) < 0.01 
                for p in existing_positions
            )
            
            if not already_exists and entry_price_to_save > 0:
                # Добавляем новую позицию
                amount_crypto = self.current_position_size_usdt / entry_price_to_save if entry_price_to_save > 0 else 0
                add_position(
                    current_symbol,
                    entry_price_to_save,
                    self.current_position_size_usdt,
                    amount_crypto,
                    order_id=None
                )
                log_info(f"✅ Новая позиция #{pair_data.get('next_position_id', 1)} добавлена для {current_symbol}")
            else:
                # Позиция уже есть, просто загружаем state
                log_info(f"📊 Позиция для {current_symbol} уже существует, пропускаем добавление")
        else:
            # Позиция закрыта - закрываем все позиции для пары
            close_all_positions(current_symbol)
            log_info(f"✅ Все позиции для {current_symbol} закрыты")
        
        log_info(f"💾 Состояние позиции для {current_symbol} обновлено")

    def _load_position_background(self):
        """Фоновая загрузка состояния позиции - не блокирует старт"""
        log_info("🔄 Фоновая загрузка позиций...")
        self.load_position_state()
        self._position_loaded = True
        log_info("✅ Позиции загружены в фоне")

    def load_position_state(self):
        """Загружает состояние позиции из файла для текущей пары и проверяет реальные позиции на KuCoin"""
        try:
            symbol = self.settings.trading_pairs['active_pair']
            strategy = self.get_active_strategy()
            position_loaded_from_file = False
            
            # 🔧 ИЗМЕНЕНИЕ: Загружаем позицию для текущей пары из словаря позиций
            if os.path.exists('position_state.json'):
                with open('position_state.json', 'r') as f:
                    data = json.load(f)
                
                # Определяем формат файла
                state = None
                if isinstance(data, dict):
                    if 'symbol' in data and 'position' in data:
                        # Старый формат (одна позиция) - используем только если это та же пара
                        if data.get('symbol') == symbol:
                            state = data
                    else:
                        # Новый формат (словарь позиций по парам) - загружаем позицию для текущей пары
                        state = data.get(symbol)
                
                if state:
                    self.position = state.get('position')
                    # 🔧 ПРИОРИТЕТ: используем entry_price из стратегии, если он есть, иначе из бота
                    strategy_entry_price = state.get('strategy_entry_price', 0)
                    bot_entry_price = state.get('entry_price', 0)
                    self.entry_price = strategy_entry_price if strategy_entry_price > 0 else bot_entry_price
                    self.current_position_size_usdt = state.get('position_size_usdt', 0)
                    self.last_trade_time = state.get('opened_at', 0)
                    
                    # 🔧 ВОССТАНАВЛИВАЕМ ПОЛНОЕ СОСТОЯНИЕ В СТРАТЕГИИ (критично!)
                    strategy_position_size = state.get('strategy_position_size_usdt', 0)
                    
                    if self.position == 'long' and self.entry_price > 0:
                        # Восстанавливаем позицию в стратегии
                        strategy.position = 'long'
                        strategy.entry_price = self.entry_price
                        strategy.position_size_usdt = strategy_position_size if strategy_position_size > 0 else self.current_position_size_usdt
                        # Восстанавливаем время открытия, если оно есть
                        if self.last_trade_time > 0:
                            if hasattr(strategy, 'position_opened_at'):
                                strategy.position_opened_at = self.last_trade_time
                            if hasattr(strategy, 'highest_price_since_entry'):
                                strategy.highest_price_since_entry = self.entry_price
                        
                        log_info(f"✅ Восстановлена открытая позиция для {symbol} из файла: вход {self.entry_price:.2f} USDT, размер {strategy.position_size_usdt:.2f} USDT")
                        log_info(f"✅ Состояние стратегии восстановлено: position={strategy.position}, entry_price={strategy.entry_price:.2f}")
                        position_loaded_from_file = True
                    elif self.position == 'long':
                        # Если позиция помечена как 'long', но нет entry_price - это проблема
                        log_error(f"⚠️ Позиция помечена как 'long', но entry_price={self.entry_price}. Проверяем реальное состояние на бирже...")
                        self.position = None
                        self.entry_price = 0
                        self.current_position_size_usdt = 0
                        strategy.position = None
                        strategy.entry_price = 0
                        strategy.position_size_usdt = 0
                    elif strategy_position_size > 0:
                        # Если есть размер позиции, но нет полных данных - сбрасываем
                        strategy.position_size_usdt = strategy_position_size
                else:
                    # Нет сохраненной позиции для этой пары - сбрасываем состояние
                    log_info(f"📋 Нет сохраненной позиции для {symbol} - начинаем с чистого листа")
                    self.position = None
                    self.entry_price = 0
                    self.current_position_size_usdt = 0
                    strategy.position = None
                    strategy.entry_price = 0
                    strategy.position_size_usdt = 0
            
            # 🔍 КРИТИЧНО: ВСЕГДА проверяем реальное состояние на KUCOIN и обновляем цену входа
            # Это гарантирует, что используется максимальная цена среди открытых покупок (после последней продажи)
            if self.exchange.connected:
                log_info("🔍 Проверяю открытые позиции на KuCoin...")
                
                # Получаем все открытые покупки (после последней продажи) и максимальную цену
                existing_buy_trades, max_existing_price = self.exchange.get_open_buy_trades_after_last_sell(symbol)
                
                position_info = self.exchange.check_open_position(symbol)
                
                if position_info.get('has_position'):
                    # Обнаружена реальная открытая позиция на бирже
                    self.position = position_info['position_type']
                    
                    # 🔧 КРИТИЧНО: Используем максимальную цену среди открытых покупок (после последней продажи)
                    # Это гарантирует правильную цену входа, даже если в файле была сохранена старая цена
                    if max_existing_price > 0:
                        self.entry_price = max_existing_price
                        log_info(f"   ✅ Обновлена цена входа на максимальную среди открытых покупок: {self.entry_price:.2f} USDT")
                        if existing_buy_trades:
                            log_info(f"   📊 Найдено открытых покупок после последней продажи: {len(existing_buy_trades)}")
                    elif position_info.get('entry_price'):
                        # Если не удалось получить через новый метод, используем из check_open_position
                        self.entry_price = position_info['entry_price']
                        log_info(f"   ⚠️ Используется цена входа из check_open_position: {self.entry_price:.2f} USDT")
                    else:
                        # Если цена не найдена, но есть позиция - используем сохраненную из файла (если есть)
                        if self.entry_price == 0:
                            log_error("⚠️ Не удалось определить цену входа из истории сделок")
                    
                    # 🔧 КРИТИЧНО: Размер позиции всегда рассчитывается из настроек (ставка), а не из суммы покупок
                    # Размер позиции = размер одной ставки из настроек (но не меньше минимального)
                    balance = self.exchange.get_balance()
                    if balance:
                        trade_amount_percent = self.settings.settings['trade_amount_percent']
                        initial_position_size_usdt = balance['free_usdt'] * trade_amount_percent
                        # Получаем минимальный размер ставки
                        min_amount = self.get_min_amount(symbol)
                        # Получаем EMA периоды из стратегии
                        strategy = self.get_active_strategy()
                        ema_fast = strategy.settings.get('ema_fast_period', 9)
                        ema_slow = strategy.settings.get('ema_slow_period', 21)
                        market_data_check = self.exchange.get_market_data(symbol, ema_fast_period=ema_fast, ema_slow_period=ema_slow)
                        if market_data_check:
                            min_position_usdt = min_amount * market_data_check['current_price']
                            # Используем расчетный размер или минимальный (если расчетный меньше)
                            calculated_position_size = max(initial_position_size_usdt, min_position_usdt)
                            # Но не меньше 0.1 USDT (минимум KuCoin)
                            self.current_position_size_usdt = max(calculated_position_size, 0.1)
                            log_info(f"   📊 Размер позиции рассчитан из настроек: {self.current_position_size_usdt:.2f} USDT")
                            log_info(f"      (ставка: {trade_amount_percent*100:.1f}% = {initial_position_size_usdt:.2f} USDT, минимум: {min_position_usdt:.2f} USDT)")
                        else:
                            # Если не удалось получить рыночные данные, используем расчетный размер или минимальный
                            self.current_position_size_usdt = max(initial_position_size_usdt, 0.1)
                            log_info(f"   📊 Размер позиции (из расчетного): {self.current_position_size_usdt:.2f} USDT")
                    else:
                        # Если не удалось получить баланс, используем минимальный размер
                        self.current_position_size_usdt = 0.1  # Минимум KuCoin
                        log_info(f"   ⚠️ Не удалось получить баланс, используем минимальный размер: {self.current_position_size_usdt:.2f} USDT")
                    
                    # Используем время последней сделки, если есть
                    last_trade = position_info.get('last_trade')
                    if last_trade and last_trade.get('timestamp'):
                        self.last_trade_time = last_trade['timestamp']
                    else:
                        self.last_trade_time = int(time.time() * 1000)  # Текущее время в миллисекундах
                    
                    # Восстанавливаем позицию в стратегии
                    strategy.position = self.position
                    strategy.entry_price = self.entry_price
                    strategy.position_size_usdt = self.current_position_size_usdt
                    log_info(f"   📊 Размер позиции установлен в стратегии: {strategy.position_size_usdt:.2f} USDT")
                    
                    # Восстанавливаем время открытия
                    if self.last_trade_time > 0:
                        if hasattr(strategy, 'position_opened_at'):
                            strategy.position_opened_at = self.last_trade_time
                        if hasattr(strategy, 'highest_price_since_entry'):
                            strategy.highest_price_since_entry = self.entry_price
                    
                    # ⚠️ НЕ СОХРАНЯЕМ при инициализации - только читаем из файла!
                    # Сохранение происходит только при реальных сделках в execute_trade()
                    # self.save_position_state()  # ОТКЛЮЧЕНО - не создаем дубликаты при старте
                    
                    log_info(f"✅ Обнаружена и восстановлена открытая позиция на KuCoin:")
                    log_info(f"   • Баланс: {position_info['base_balance']:.8f} {symbol.split('/')[0]}")
                    log_info(f"   • Цена входа (максимальная среди открытых покупок): {self.entry_price:.2f} USDT")
                    log_info(f"   • Размер позиции: {self.current_position_size_usdt:.2f} USDT")
                elif position_info.get('has_position') and not position_info.get('entry_price'):
                    # Есть баланс, но не удалось определить цену входа
                    log_info(f"⚠️ Обнаружен баланс {position_info['base_balance']:.8f} {symbol.split('/')[0]}, но не удалось определить цену входа из истории сделок")
                else:
                    # Нет открытой позиции на бирже
                    if self.position is None:
                        log_info("✅ Нет открытых позиций на KuCoin")
                    else:
                        # В файле была позиция, но на бирже её нет - сбрасываем
                        log_info("⚠️ Позиция в файле не соответствует реальному состоянию на бирже. Сбрасываем состояние.")
                        self.position = None
                        self.entry_price = 0
                        self.current_position_size_usdt = 0
                        strategy.position = None
                        strategy.entry_price = 0
                        strategy.position_size_usdt = 0
                        self.save_position_state()
                        
        except Exception as e:
            log_error(f"❌ Ошибка загрузки состояния позиции: {e}")

    def save_strategy_settings(self):
        """Сохраняет настройки стратегии"""
        try:
            self.settings.save_strategy_settings()
            log_info("💾 Настройки стратегии сохранены")
        except Exception as e:
            log_error(f"❌ Ошибка сохранения настроек стратегии: {e}")

    def get_take_profit_info(self):
        """Получение информации о текущих настройках Take Profit"""
        return self.settings.get_take_profit_info()

    def reset_settings_to_default(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            success = self.settings.reset_to_defaults()
            if success:
                log_info("🔄 Настройки сброшены к значениям по умолчанию")
                # Обновляем настройки в активной стратегии
                strategy = self.get_active_strategy()
                if strategy:
                    strategy.settings['take_profit_usdt'] = 0.0
                    strategy.settings['take_profit_percent'] = 2.0
                return True
            else:
                log_error("❌ Не удалось сбросить настройки")
                return False
        except Exception as e:
            log_error(f"❌ Ошибка сброса настроек: {e}")
            return False