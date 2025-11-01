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