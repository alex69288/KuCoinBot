"""
РАБОТА С БИРЖЕЙ KUCOIN
"""
import ccxt
import os
import time
import traceback
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from utils.logger import log_info, log_error
import threading

load_dotenv()

class ExchangeManager:
    def __init__(self):
        self.exchange = None
        self.connected = False
        self.markets_loaded = threading.Event() # Событие для синхронизации
        self.connect()

    def _load_markets_background(self):
        """Загружает рынки в фоновом потоке."""
        try:
            print("🔄 Фоновая загрузка рынков...", flush=True)
            self.exchange.load_markets(reload=True)
            self.markets_loaded.set() # Устанавливаем флаг, что рынки загружены
            print(f"✅ Рынки загружены в фоне ({len(self.exchange.markets)} пар)", flush=True)
        except Exception as e:
            log_error(f"❌ Ошибка фоновой загрузки рынков: {e}")
            self.markets_loaded.set() # Устанавливаем флаг даже при ошибке, чтобы не блокировать вечно

    def connect(self):
        """Подключение к бирже KuCoin с диагностикой переменных окружения и повторными попытками."""
        api_key = os.getenv('KUCOIN_API_KEY')
        secret_key = os.getenv('KUCOIN_SECRET_KEY')
        passphrase = os.getenv('KUCOIN_PASSPHRASE')
        missing = [n for n, v in [('KUCOIN_API_KEY', api_key), ('KUCOIN_SECRET_KEY', secret_key), ('KUCOIN_PASSPHRASE', passphrase)] if not v]
        if missing:
            log_error(f"⚠️ Отсутствуют переменные окружения: {', '.join(missing)}. Публичные данные можно получать без них, но баланс/торговля недоступны.")

        base_config = {
            'apiKey': api_key or '',
            'secret': secret_key or '',
            'password': passphrase or '',
            'sandbox': False,
            'enableRateLimit': True,
            'rateLimit': 300,
            'timeout': 30000,
        }
        proxy = os.getenv('PROXY_URL')
        if proxy:
            base_config['proxies'] = {'http': proxy, 'https': proxy}
            log_info(f"🔒 Использую прокси: {proxy.split('@')[-1] if '@' in proxy else proxy}")

        # Повторные попытки подключения (например, временные сетевые проблемы)
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                print(f"🔌 Попытка {attempt}/{attempts}: Создание клиента KuCoin...", flush=True)
                self.exchange = ccxt.kucoin(base_config)
                
                # ⚡ ОПТИМИЗАЦИЯ: Запускаем загрузку рынков в фоне
                threading.Thread(target=self._load_markets_background, daemon=True).start()
                
                print(f"✅ Клиент создан, рынки загружаются в фоне...", flush=True)
                
                # Баланс пробуем только если есть ключи (легкий запрос)
                if api_key and secret_key and passphrase:
                    self.exchange.fetch_balance()
                self.connected = True
                log_info(f"✅ Успешное подключение к KuCoin (попытка {attempt}/{attempts})")
                return
            except ccxt.AuthenticationError as e:
                log_error(f"❌ Ошибка аутентификации KuCoin (попытка {attempt}): {e}")
                break  # нет смысла повторять
            except ccxt.NetworkError as e:
                log_error(f"🌐 Сетевая ошибка подключения KuCoin (попытка {attempt}): {e}")
            except ccxt.ExchangeNotAvailable as e:
                log_error(f"🚫 Биржа недоступна KuCoin (попытка {attempt}): {e}")
            except ccxt.ExchangeError as e:
                log_error(f"❌ Ошибка биржи KuCoin (попытка {attempt}): {e}")
            except Exception as e:
                log_error(f"❌ Непредвиденная ошибка подключения (попытка {attempt}): {e}\n{traceback.format_exc()}")
            time.sleep(2 * attempt)  # экспоненциальная задержка

        self.connected = False
        log_error("❌ Подключение к KuCoin не удалось после всех попыток")

    def wait_for_markets(self, timeout=60):
        """Ожидает завершения загрузки рынков."""
        loaded = self.markets_loaded.wait(timeout)
        if not loaded:
            log_error(f"⌛️ Превышен таймаут ({timeout}s) ожидания загрузки рынков.")
            return False
        return True

    def get_balance(self):
        """Получение баланса"""
        if not self.connected:
            return None
            
        try:
            balance = self.exchange.fetch_balance()
            return {
                'total_usdt': balance['total'].get('USDT', 0),
                'free_usdt': balance['free'].get('USDT', 0),
                'used_usdt': balance['used'].get('USDT', 0),
                'total_btc': balance['total'].get('BTC', 0),
                'free_btc': balance['free'].get('BTC', 0),
            }
        except Exception as e:
            log_error(f"❌ Ошибка получения баланса: {e}")
            return None
    
    def get_market_data(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 50,
        ema_fast_period: int = 9,
        ema_slow_period: int = 21,
        retries: int = 3,
    ):
        """Получение и кэширование рыночных данных (OHLCV, EMA, и т.д.)"""
        if not self.wait_for_markets():
            return None # Возвращаем None, если рынки не загрузились
            
        # Проверяем, есть ли символ в загруженных рынках
        if symbol not in self.exchange.markets:
            log_error(f"❌ Символ {symbol} не найден в markets KuCoin")
            return None

        last_exception = None
        for attempt in range(1, retries + 1):
            start_t = time.time()
            try:
                log_info(f"🔄 Запрос OHLCV {symbol} timeframe={timeframe} limit={limit} (попытка {attempt}/{retries})")
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                duration = (time.time() - start_t) * 1000
                if not ohlcv or len(ohlcv) < 2:
                    log_error(f"⚠️ Пустой или недостаточный OHLCV ответ (len={len(ohlcv) if ohlcv else 0}) за {duration:.1f} ms")
                    last_exception = ValueError("Недостаточно свечей")
                else:
                    closes = [candle[4] for candle in ohlcv]
                    current_price = closes[-1]
                    from utils.helpers import calculate_ema
                    fast_ema = calculate_ema(closes, ema_fast_period)
                    slow_ema = calculate_ema(closes, ema_slow_period)
                    ema_diff_percent = (fast_ema - slow_ema) / slow_ema if slow_ema else 0
                    price_change_24h = 0
                    if len(closes) >= 24:
                        price_24h_ago = closes[-24]
                        if price_24h_ago:
                            price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
                    data = {
                        'fast_ema': fast_ema,
                        'slow_ema': slow_ema,
                        'ema_diff_percent': ema_diff_percent,
                        'current_price': current_price,
                        'price_change_24h': price_change_24h,
                        'ohlcv': ohlcv,
                        'latency_ms': duration
                    }
                    log_info(f"✅ OHLCV получен: {len(ohlcv)} свечей, latency={duration:.1f} ms, цена={current_price}")
                    return data
            except ccxt.NetworkError as e:
                last_exception = e
                log_error(f"🌐 Сетевая ошибка OHLCV {symbol} (попытка {attempt}): {e}")
            except ccxt.ExchangeError as e:
                last_exception = e
                log_error(f"❌ Ошибка биржи OHLCV {symbol} (попытка {attempt}): {e}")
            except Exception as e:
                last_exception = e
                log_error(f"❌ Непредвиденная ошибка OHLCV {symbol} (попытка {attempt}): {e}\n{traceback.format_exc()}")
            # Задержка перед повтором (экспоненциальная)
            if attempt < retries:
                delay = 2 ** attempt
                time.sleep(delay)
                log_info(f"⏳ Повторная попытка через {delay:.1f} сек...")

        log_error(f"❌ Не удалось получить рыночные данные {symbol} после {retries} попыток: {last_exception}")
        return None
    
    def get_ticker(self, symbol):
        """Получение тикера"""
        if not self.wait_for_markets():
            return None
            
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            
            # Защита от None значений
            change = ticker.get('percentage', 0)
            if change is None:
                log_error(f"⚠️ ticker['percentage'] is None для {symbol}, используем 0")
                change = 0
            
            return {
                'symbol': symbol,
                'last': ticker.get('last', 0) or 0,
                'high': ticker.get('high', 0) or 0,
                'low': ticker.get('low', 0) or 0,
                'volume': ticker.get('baseVolume', 0) or 0,
                'change': change,
                'timestamp': ticker.get('timestamp', 0) or 0
            }
        except Exception as e:
            log_error(f"❌ Ошибка получения тикера {symbol}: {e}")
            return None
    
    def create_order(self, symbol, order_type, side, amount, price=None):
        """Создание ордера с проверкой минимального объема"""
        if not self.wait_for_markets():
            return None, "Рынки не загружены"
            
        try:
            # 🔧 ПОЛУЧАЕМ ИНФОРМАЦИЮ О РЫНКЕ ДЛЯ ПРОВЕРКИ МИНИМАЛЬНОГО ОБЪЕМА
            market = self.exchange.market(symbol)
            min_amount = market['limits']['amount']['min']
            min_cost = market['limits']['cost']['min']  # Минимальная сумма в quote currency (USDT)
            
            log_info(f"🔍 Проверка ордера: amount={amount:.6f}, min_amount={min_amount}, min_cost={min_cost}")
            
            # Проверяем минимальное количество
            if amount < min_amount:
                error_msg = f"Количество {amount:.6f} меньше минимального {min_amount}"
                log_error(f"❌ {error_msg}")
                return None, error_msg
                
            # Проверяем минимальную сумму ордера
            current_price = self.get_ticker(symbol)['last'] if not price else price
            order_cost = amount * current_price
            
            if order_cost < min_cost:
                error_msg = f"Сумма ордера {order_cost:.2f} USDT меньше минимальной {min_cost} USDT"
                log_error(f"❌ {error_msg}")
                return None, error_msg
            
            # 🔧 СОЗДАЕМ ОРДЕР
            if order_type == 'market':
                order = self.exchange.create_order(symbol, 'market', side, amount)
            else:
                order = self.exchange.create_order(symbol, 'limit', side, amount, price)
            
            log_info(f"✅ Ордер создан: {side} {amount:.6f} {symbol} (сумма: {order_cost:.2f} USDT)")
            return order, "Успешно"
            
        except ccxt.InsufficientFunds as e:
            error_msg = f"❌ Недостаточно средств для создания ордера: {e}"
            log_error(error_msg)
            return None, error_msg
        except ccxt.InvalidOrder as e:
            error_msg = f"❌ Неверные параметры ордера: {e}"
            log_error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ Ошибка создания ордера: {e}"
            log_error(error_msg)
            return None, error_msg
    
    def get_order_status(self, order_id, symbol):
        """Получение статуса ордера"""
        if not self.wait_for_markets():
            return None
            
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            log_error(f"❌ Ошибка получения статуса ордера {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """Отмена ордера"""
        if not self.wait_for_markets():
            return False
            
        try:
            self.exchange.cancel_order(order_id, symbol)
            log_info(f"✅ Ордер отменен: {order_id}")
            return True
        except Exception as e:
            log_error(f"❌ Ошибка отмены ордера {order_id}: {e}")
            return False
    
    def get_open_orders(self, symbol=None):
        """Получение открытых ордеров"""
        if not self.wait_for_markets():
            return []
            
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            log_error(f"❌ Ошибка получения открытых ордеров: {e}")
            return []
    
    def get_market_info(self, symbol):
        """Получение информации о рынке"""
        if not self.wait_for_markets():
            return None
            
        try:
            market = self.exchange.market(symbol)
            return {
                'symbol': symbol,
                'base': market['base'],
                'quote': market['quote'],
                'min_amount': market['limits']['amount']['min'],
                'max_amount': market['limits']['amount']['max'],
                'min_cost': market['limits']['cost']['min'],
                'max_cost': market['limits']['cost']['max'],
                'price_precision': market['precision']['price'],
                'amount_precision': market['precision']['amount']
            }
        except Exception as e:
            log_error(f"❌ Ошибка получения информации о рынке {symbol}: {e}")
            return None

    def get_min_limits(self, symbol):
        """Возвращает (min_amount, min_cost) для пары с безопасными fallback.
        - min_amount: минимальное количество базовой валюты (BTC/SOL/...)
        - min_cost: минимальная сумма ордера в котируемой валюте (обычно USDT)
        """
        if not self.wait_for_markets():
            # Безопасные значения по умолчанию, если рынки не загружены
            from config.constants import MIN_TRADE_USDT
            return 0.001, MIN_TRADE_USDT
            
        try:
            if self.connected:
                market = self.exchange.market(symbol)
                min_amount = market['limits']['amount']['min'] or 0
                min_cost = market['limits']['cost']['min'] or 0.1
            else:
                # Fallback: используем константы проекта
                from config.constants import MIN_TRADE_AMOUNTS, MIN_TRADE_USDT
                min_amount = MIN_TRADE_AMOUNTS.get(symbol, 0.001)
                min_cost = MIN_TRADE_USDT
            return float(min_amount), float(min_cost)
        except Exception as e:
            log_error(f"❌ Ошибка получения минимальных лимитов {symbol}: {e}")
            # Безопасные значения по умолчанию
            from config.constants import MIN_TRADE_USDT
            return 0.001, MIN_TRADE_USDT
    
    def fetch_my_trades(self, symbol, limit=500, days_back=60):
        """Получение истории сделок пользователя с расширенным окном по времени и параметрами KuCoin.
        - limit: желаемое максимальное количество сделок (до 500 за страницу)
        - days_back: сколько дней назад начинать выборку (по умолчанию 60)
        """
        if not self.wait_for_markets():
            return []
            
        try:
            # Начало окна выборки
            since_ms = int((time.time() - days_back * 86400) * 1000)

            # Параметры, специфичные для KuCoin (см. /api/v1/fills: pageSize/startAt/endAt)
            params = {}
            page_size = 500 if (limit is None or limit > 500) else int(limit)
            if getattr(self.exchange, 'id', '') == 'kucoin':
                params['pageSize'] = page_size
                params['startAt'] = since_ms // 1000  # сек

            collected = []
            remaining = limit or page_size
            max_pages = 3  # защитный предел пагинации
            end_at_sec = None

            for _ in range(max_pages):
                call_params = dict(params)
                if end_at_sec is not None:
                    # Пагинация назад по времени: берём до endAt
                    call_params['endAt'] = end_at_sec

                # 🔧 ИСПРАВЛЕНИЕ: KuCoin не работает с since + startAt одновременно
                # Используем ЛИБО since (ccxt), ЛИБО startAt (kucoin params)
                batch = self.exchange.fetch_my_trades(
                    symbol,
                    since=None,  # Не передаем since, используем только params
                    limit=min(page_size, remaining),
                    params=call_params,
                )
                
                log_info(f"🔍 DEBUG fetch_my_trades: API вернул {len(batch) if batch else 0} сделок для {symbol}, params={call_params}")

                if not batch:
                    break

                collected.extend(batch)

                # Если получили меньше страницы — дальше нечего запрашивать
                if len(batch) < min(page_size, remaining):
                    break

                # Готовим endAt для следующей страницы (строго раньше самой старой сделки из batch)
                oldest_ts_ms = min(t.get('timestamp', since_ms) for t in batch)
                end_at_sec = max(0, (oldest_ts_ms // 1000) - 1)

                # Контроль общего лимита
                if limit is not None:
                    remaining = max(0, remaining - len(batch))
                    if remaining == 0:
                        break

            # Сортируем по времени (от старых к новым)
            collected.sort(key=lambda x: x['timestamp'])
            # Лог: сколько всего собрали
            log_info(f"🔍 DEBUG: fetch_my_trades: собрано {len(collected)} сделок за ~{days_back} дней (limit={limit}, page_size={page_size})")
            return collected
        except Exception as e:
            log_error(f"❌ Ошибка получения истории сделок {symbol}: {e}")
            return []
    
    def get_open_buy_trades_after_last_sell(self, symbol):
        """
        Получает все открытые покупки (покупки после последней продажи)
        Возвращает список покупок и максимальную цену среди них
        """
        if not self.wait_for_markets():
            return [], 0.0
        
        try:
            # Берём расширенную историю (уже отсортирована)
            trades = self.fetch_my_trades(symbol, limit=500)
            if not trades:
                return [], 0.0
            
            # Логирование для отладки - показываем ВСЕ полученные сделки
            from utils.logger import log_info
            log_info(f"🔍 DEBUG: Всего получено сделок из API: {len(trades)}")
            for i, trade in enumerate(trades, 1):
                log_info(f"   DEBUG Сделка {i}: {trade['side'].upper()} по {trade.get('price', 0):.2f} USDT, время: {trade.get('timestamp', 0)}")
            
            # Ищем последнюю продажу
            last_sell_time = 0
            last_sell_index = -1
            for i, trade in enumerate(reversed(trades)):
                if trade['side'] == 'sell':
                    last_sell_time = trade['timestamp']
                    last_sell_index = len(trades) - 1 - i
                    log_info(f"🔍 DEBUG: Найдена последняя продажа на индексе {last_sell_index}, timestamp: {last_sell_time}")
                    break
            
            if last_sell_index < 0:
                log_info(f"🔍 DEBUG: Продажи не найдено, берем все покупки")
            
            # УПРОЩЕННЫЙ АЛГОРИТМ: просто берем все покупки ПОСЛЕ последней продажи
            # Это работает для большинства случаев и проще в отладке
            buy_trades = []
            
            if last_sell_index >= 0:
                # Берем все покупки после последней продажи
                for trade in trades:
                    if trade['side'] == 'buy' and trade['timestamp'] > last_sell_time:
                        buy_trades.append({
                            'price': trade.get('price', 0.0),
                            'amount': trade.get('amount', 0.0),
                            'timestamp': trade.get('timestamp', 0),
                            'cost': trade.get('cost', 0) or (trade.get('amount', 0) * trade.get('price', 0))
                        })
            else:
                # Если продаж не было, берем все покупки
                for trade in trades:
                    if trade['side'] == 'buy':
                        buy_trades.append({
                            'price': trade.get('price', 0.0),
                            'amount': trade.get('amount', 0.0),
                            'timestamp': trade.get('timestamp', 0),
                            'cost': trade.get('cost', 0) or (trade.get('amount', 0) * trade.get('price', 0))
                        })
            
            log_info(f"🔍 DEBUG: Открытых покупок после последней продажи: {len(buy_trades)}")
            for i, bt in enumerate(buy_trades, 1):
                log_info(f"   DEBUG LOT {i}: {bt['amount']:.8f} BTC @ {bt['price']:.2f} USDT (стоимость {bt.get('cost', 0):.2f} USDT) ts={bt['timestamp']}")
            
            log_info(f"🔍 Открытые позиции: найдено {len(buy_trades)} покупок после последней продажи (timestamp: {last_sell_time})")
            
            # Находим максимальную цену среди открытых покупок
            max_price = 0.0
            if buy_trades:
                max_price_trade = max(buy_trades, key=lambda t: t.get('price', 0))
                max_price = max_price_trade.get('price', 0)
            
            return buy_trades, max_price
            
        except Exception as e:
            log_error(f"❌ Ошибка получения открытых покупок {symbol}: {e}")
            import traceback
            log_error(f"   Traceback: {traceback.format_exc()}")
            return [], 0.0
    
    def check_open_position(self, symbol):
        """
        Проверка открытой позиции на KuCoin через баланс и историю сделок
        
        Возвращает словарь с информацией о позиции:
        {
            'has_position': bool,
            'position_type': 'long' или None,
            'base_balance': float,  # Баланс базовой валюты (BTC)
            'quote_balance': float,  # Баланс quote валюты (USDT)
            'last_trade': dict или None,  # Последняя сделка
            'entry_price': float или None,  # Средняя цена входа
            'position_size_usdt': float или None  # Размер позиции в USDT
        }
        """
        if not self.wait_for_markets():
            return {
                'has_position': False,
                'position_type': None,
                'base_balance': 0,
                'quote_balance': 0,
                'last_trade': None,
                'entry_price': None,
                'position_size_usdt': None
            }
        
        try:
            # Получаем баланс
            balance = self.exchange.fetch_balance()
            market = self.exchange.market(symbol)
            base_currency = market['base']  # BTC
            quote_currency = market['quote']  # USDT
            
            base_balance = balance['free'].get(base_currency, 0) + balance['used'].get(base_currency, 0)
            quote_balance = balance['free'].get(quote_currency, 0) + balance['used'].get(quote_currency, 0)
            
            # Получаем историю сделок
            trades = self.fetch_my_trades(symbol, limit=100)
            
            # Если есть баланс базовой валюты, значит есть позиция
            has_position = base_balance > 0
            
            if not has_position:
                return {
                    'has_position': False,
                    'position_type': None,
                    'base_balance': base_balance,
                    'quote_balance': quote_balance,
                    'last_trade': trades[-1] if trades else None,
                    'entry_price': None,
                    'position_size_usdt': None
                }
            
            # Если есть баланс, проверяем последние сделки
            # Находим последнюю покупку и все покупки после последней продажи
            buy_trades = []
            last_sell_time = 0
            
            # Ищем последнюю продажу
            for trade in reversed(trades):
                if trade['side'] == 'sell':
                    last_sell_time = trade['timestamp']
                    break
            
            # Собираем все покупки после последней продажи
            for trade in trades:
                if trade['timestamp'] > last_sell_time and trade['side'] == 'buy':
                    buy_trades.append(trade)
            
            # Если нет покупок после последней продажи, но есть баланс - берем последнюю покупку
            if not buy_trades and trades:
                for trade in reversed(trades):
                    if trade['side'] == 'buy':
                        buy_trades.append(trade)
                        break
            
            if not buy_trades:
                # Если нет покупок в истории, но есть баланс - используем текущую цену как приблизительную
                ticker = self.get_ticker(symbol)
                entry_price = ticker['last'] if ticker else None
                position_size_usdt = base_balance * entry_price if entry_price else None
                
                log_info(f"⚠️ Обнаружен баланс {base_balance} {base_currency}, но нет истории покупок. Используем текущую цену.")
                
                return {
                    'has_position': True,
                    'position_type': 'long',
                    'base_balance': base_balance,
                    'quote_balance': quote_balance,
                    'last_trade': trades[-1] if trades else None,
                    'entry_price': entry_price,
                    'position_size_usdt': position_size_usdt
                }
            
            # Находим максимальную цену среди открытых сделок (покупок после последней продажи)
            # Это защищает от убытков по более дешевым покупкам - все позиции закрываются по максимальной цене + take profit
            if buy_trades:
                # Находим максимальную цену покупки
                max_price_trade = max(buy_trades, key=lambda t: t.get('price', 0))
                entry_price = max_price_trade.get('price', 0)
                
                # Используем последнюю покупку для получения времени
                last_buy = buy_trades[-1]
                
                log_info(f"✅ Обнаружена открытая позиция: {base_balance} {base_currency}")
                log_info(f"   • Максимальная цена входа (из {len(buy_trades)} покупок): {entry_price:.2f} USDT")
                if len(buy_trades) > 1:
                    # Показываем детали по каждой покупке
                    total_invested = sum(
                        trade.get('cost', 0) or (trade.get('amount', 0) * trade.get('price', 0))
                        for trade in buy_trades
                    )
                    log_info(f"   • Общая сумма инвестиций: {total_invested:.2f} USDT (из {len(buy_trades)} покупок)")
                    for i, trade in enumerate(buy_trades, 1):
                        trade_cost = trade.get('cost', 0) or (trade.get('amount', 0) * trade.get('price', 0))
                        log_info(f"      Покупка {i}: {trade.get('price', 0):.2f} USDT × {trade.get('amount', 0):.8f} = {trade_cost:.2f} USDT")
                
                # 🔧 Размер позиции НЕ рассчитывается здесь - он должен быть из настроек (ставка)
                # Устанавливаем None, чтобы размер позиции рассчитывался из настроек при восстановлении
                position_size_usdt = None
                
                return {
                    'has_position': True,
                    'position_type': 'long',
                    'base_balance': base_balance,
                    'quote_balance': quote_balance,
                    'last_trade': last_buy,
                    'entry_price': entry_price,
                    'position_size_usdt': position_size_usdt
                }
            else:
                return {
                    'has_position': False,
                    'position_type': None,
                    'base_balance': base_balance,
                    'quote_balance': quote_balance,
                    'last_trade': trades[-1] if trades else None,
                    'entry_price': None,
                    'position_size_usdt': None
                }
                
        except Exception as e:
            log_error(f"❌ Ошибка проверки открытой позиции {symbol}: {e}")
            return {
                'has_position': False,
                'position_type': None,
                'base_balance': 0,
                'quote_balance': 0,
                'last_trade': None,
                'entry_price': None,
                'position_size_usdt': None
            }