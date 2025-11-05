"""
РАБОТА С БИРЖЕЙ KUCOIN
"""
import ccxt
import os
from dotenv import load_dotenv
from utils.logger import log_info, log_error

load_dotenv()

class ExchangeManager:
    def __init__(self):
        self.exchange = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Подключение к бирже KuCoin"""
        try:
            self.exchange = ccxt.kucoin({
                'apiKey': os.getenv('KUCOIN_API_KEY'),
                'secret': os.getenv('KUCOIN_SECRET_KEY'),
                'password': os.getenv('KUCOIN_PASSPHRASE'),
                'sandbox': False,
                'enableRateLimit': True,
                'rateLimit': 300,
                'timeout': 30000,
            })
            
            # Проверяем подключение
            self.exchange.fetch_balance()
            self.connected = True
            log_info("✅ Успешное подключение к KuCoin")
            
        except ccxt.AuthenticationError as e:
            log_error(f"❌ Ошибка аутентификации KuCoin: {e}")
            self.connected = False
        except ccxt.ExchangeError as e:
            log_error(f"❌ Ошибка биржи KuCoin: {e}")
            self.connected = False
        except Exception as e:
            log_error(f"❌ Ошибка подключения к KuCoin: {e}")
            self.connected = False
    
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
    
    def get_market_data(self, symbol, timeframe='1h', limit=50):
        """Получение рыночных данных"""
        if not self.connected:
            return None
            
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv or len(ohlcv) < 2:
                return None
            
            closes = [candle[4] for candle in ohlcv]
            current_price = closes[-1]
            
            # Рассчитываем индикаторы
            from utils.helpers import calculate_ema
            
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
                'ohlcv': ohlcv
            }
            
        except Exception as e:
            log_error(f"❌ Ошибка получения данных для {symbol}: {e}")
            return None
    
    def get_ticker(self, symbol):
        """Получение тикера"""
        if not self.connected:
            return None
            
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'change': ticker['percentage'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            log_error(f"❌ Ошибка получения тикера {symbol}: {e}")
            return None
    
    def create_order(self, symbol, order_type, side, amount, price=None):
        """Создание ордера с проверкой минимального объема"""
        if not self.connected:
            return None, "Не подключено к бирже"
            
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
        if not self.connected:
            return None
            
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            log_error(f"❌ Ошибка получения статуса ордера {order_id}: {e}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """Отмена ордера"""
        if not self.connected:
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
        if not self.connected:
            return []
            
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            log_error(f"❌ Ошибка получения открытых ордеров: {e}")
            return []
    
    def get_market_info(self, symbol):
        """Получение информации о рынке"""
        if not self.connected:
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
    
    def fetch_my_trades(self, symbol, limit=100):
        """Получение истории сделок пользователя"""
        if not self.connected:
            return []
            
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            # Сортируем по времени (от старых к новым)
            trades.sort(key=lambda x: x['timestamp'])
            return trades
        except Exception as e:
            log_error(f"❌ Ошибка получения истории сделок {symbol}: {e}")
            return []
    
    def get_open_buy_trades_after_last_sell(self, symbol):
        """
        Получает все открытые покупки (покупки после последней продажи)
        Возвращает список покупок и максимальную цену среди них
        """
        if not self.connected:
            return [], 0.0
        
        try:
            trades = self.fetch_my_trades(symbol, limit=100)
            if not trades:
                return [], 0.0
            
            # Ищем последнюю продажу
            last_sell_time = 0
            for trade in reversed(trades):
                if trade['side'] == 'sell':
                    last_sell_time = trade['timestamp']
                    break
            
            # Собираем все покупки после последней продажи
            buy_trades = []
            for trade in trades:
                if trade['timestamp'] > last_sell_time and trade['side'] == 'buy':
                    buy_trades.append(trade)
            
            # Если нет покупок после последней продажи, но есть покупки - берем последнюю покупку
            if not buy_trades and trades:
                for trade in reversed(trades):
                    if trade['side'] == 'buy':
                        buy_trades.append(trade)
                        break
            
            # Находим максимальную цену среди открытых покупок
            max_price = 0.0
            if buy_trades:
                max_price_trade = max(buy_trades, key=lambda t: t.get('price', 0))
                max_price = max_price_trade.get('price', 0)
            
            return buy_trades, max_price
            
        except Exception as e:
            log_error(f"❌ Ошибка получения открытых покупок {symbol}: {e}")
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
        if not self.connected:
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