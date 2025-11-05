"""
СКРИПТ ДЛЯ СИМУЛЯЦИИ ТОРГОВЛИ В РЕАЛЬНОМ ВРЕМЕНИ (PAPER TRADING)
"""
import time
import json
from datetime import datetime
from core.exchange import ExchangeManager
from core.bot import AdvancedTradingBot
from utils.logger import log_info, log_error


class PaperTradingSimulator:
    """Симулятор торговли без реальных сделок на бирже"""
    
    def __init__(self, initial_balance=1000.0):
        """
        Инициализация симулятора
        
        Args:
            initial_balance: Начальный баланс в USDT
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.taker_fee = 0.001  # 0.1% комиссия KuCoin
        self.position = None
        self.entry_price = 0
        self.entry_balance = 0
        self.trades = []
        self.is_running = False
        
    def reset(self):
        """Сброс состояния"""
        self.balance = self.initial_balance
        self.position = None
        self.entry_price = 0
        self.entry_balance = 0
        self.trades = []
    
    def simulate_buy(self, price, size_usdt):
        """Симуляция покупки"""
        if self.position is not None:
            return False, "Позиция уже открыта"
        
        if size_usdt > self.balance:
            return False, "Недостаточно средств"
        
        # Комиссия на вход
        fee = size_usdt * self.taker_fee
        actual_cost = size_usdt + fee
        
        if actual_cost > self.balance:
            return False, "Недостаточно средств с учетом комиссии"
        
        self.position = 'long'
        self.entry_price = price
        self.entry_balance = size_usdt
        self.balance -= actual_cost
        
        log_info(f"🟢 СИМУЛЯЦИЯ BUY: {size_usdt:.2f} USDT по цене {price:.2f} USDT")
        log_info(f"   Комиссия: {fee:.2f} USDT, Остаток: {self.balance:.2f} USDT")
        
        return True, "Позиция открыта"
    
    def simulate_sell(self, price):
        """Симуляция продажи"""
        if self.position is None:
            return False, "Нет открытой позиции"
        
        # Расчет прибыли
        profit_percent = ((price - self.entry_price) / self.entry_price) * 100
        gross_profit = self.entry_balance * (profit_percent / 100)
        
        # Комиссия на выход
        exit_value = self.entry_balance + gross_profit
        fee = exit_value * self.taker_fee
        net_profit = gross_profit - (self.entry_balance * self.taker_fee) - fee
        
        # Обновление баланса
        self.balance += exit_value - fee
        
        # Сохранение сделки
        trade = {
            'timestamp': datetime.now().isoformat(),
            'entry_price': self.entry_price,
            'exit_price': price,
            'entry_balance': self.entry_balance,
            'profit_percent': profit_percent,
            'net_profit': net_profit,
            'fees': self.entry_balance * self.taker_fee + fee,
            'balance_after': self.balance
        }
        self.trades.append(trade)
        
        profit_emoji = "✅" if net_profit > 0 else "❌"
        log_info(f"{profit_emoji} СИМУЛЯЦИЯ SELL: {price:.2f} USDT")
        log_info(f"   Прибыль: {profit_percent:.2f}% ({net_profit:.2f} USDT)")
        log_info(f"   Комиссия: {fee:.2f} USDT, Баланс: {self.balance:.2f} USDT")
        
        # Сброс позиции
        self.position = None
        self.entry_price = 0
        self.entry_balance = 0
        
        return True, trade
    
    def get_current_profit(self, current_price):
        """Получение текущей прибыли по открытой позиции"""
        if self.position is None:
            return None
        
        profit_percent = ((current_price - self.entry_price) / self.entry_price) * 100
        gross_profit = self.entry_balance * (profit_percent / 100)
        fees = self.entry_balance * self.taker_fee * 2
        net_profit = gross_profit - fees
        
        return {
            'profit_percent': profit_percent,
            'net_profit': net_profit,
            'current_balance': self.balance + net_profit
        }
    
    def get_statistics(self):
        """Получение статистики"""
        if not self.trades:
            return {
                'total_profit': 0,
                'total_profit_percent': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'win_rate': 0
            }
        
        total_profit = self.balance - self.initial_balance
        total_profit_percent = (total_profit / self.initial_balance) * 100
        
        winning_trades = [t for t in self.trades if t['net_profit'] > 0]
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.balance,
            'total_profit': total_profit,
            'total_profit_percent': total_profit_percent,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'win_rate': (len(winning_trades) / len(self.trades) * 100) if self.trades else 0
        }


class PaperTradingBot:
    """Бот для симуляции торговли"""
    
    def __init__(self, initial_balance=1000.0):
        """Инициализация бота с симулятором"""
        self.simulator = PaperTradingSimulator(initial_balance)
        
        # Создаем реальный бот, но перехватываем его операции
        self.bot = AdvancedTradingBot()
        
        # Сохраняем оригинальные методы
        self.original_create_order = self.bot.exchange.create_order
        self.original_get_balance = self.bot.exchange.get_balance
        
        # Перехватываем методы
        self.bot.exchange.create_order = self.simulate_order
        self.bot.exchange.get_balance = self.simulate_get_balance
        
        log_info("🧪 Paper Trading режим активирован")
        log_info(f"💰 Начальный баланс: {initial_balance:.2f} USDT")
    
    def simulate_get_balance(self):
        """Симуляция получения баланса"""
        # Получаем текущую прибыль по открытой позиции
        current_profit = 0
        if self.simulator.position == 'long':
            ticker = self.bot.exchange.get_ticker(self.bot.settings.trading_pairs['active_pair'])
            if ticker:
                profit_info = self.simulator.get_current_profit(ticker['last'])
                if profit_info:
                    current_profit = profit_info['net_profit']
        
        # Возвращаем баланс с учетом текущей прибыли
        balance_usdt = self.simulator.balance + current_profit
        
        return {
            'total_usdt': balance_usdt,
            'free_usdt': balance_usdt,
            'used_usdt': 0,
            'total_btc': 0,
            'free_btc': 0,
        }
    
    def simulate_order(self, symbol, order_type, side, amount, price=None):
        """Симуляция создания ордера (возвращает кортеж как в ExchangeManager)"""
        # Получаем текущую цену
        ticker = self.bot.exchange.get_ticker(symbol)
        if not ticker:
            return None, "Не удалось получить цену"
        
        current_price = ticker['last']
        
        if side == 'buy':
            size_usdt = amount * current_price
            success, message = self.simulator.simulate_buy(current_price, size_usdt)
            if not success:
                return None, message
            
            # Возвращаем фейковый ордер (кортеж как в ExchangeManager)
            order = {
                'id': f"paper_buy_{int(time.time())}",
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': current_price,
                'status': 'closed',
                'filled': amount,
                'cost': size_usdt
            }
            return order, "Успешно"
        
        elif side == 'sell':
            if self.simulator.position is None:
                return None, "Нет открытой позиции для продажи"
            
            success, trade = self.simulator.simulate_sell(current_price)
            if not success:
                return None, str(trade)
            
            # Возвращаем фейковый ордер (кортеж как в ExchangeManager)
            order = {
                'id': f"paper_sell_{int(time.time())}",
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': current_price,
                'status': 'closed',
                'filled': amount,
                'cost': self.simulator.entry_balance if hasattr(self.simulator, 'entry_balance') else 0
            }
            return order, "Успешно"
        
        return None, "Неизвестная операция"
    
    def run(self, duration_minutes=60):
        """Запуск симуляции на указанное время"""
        log_info(f"🚀 Запуск Paper Trading на {duration_minutes} минут")
        log_info("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Включаем торговлю в боте
        self.bot.settings.settings['trading_enabled'] = True
        self.bot.settings.settings['demo_mode'] = True  # Дополнительная защита
        
        try:
            while time.time() < end_time:
                # Выполняем торговый цикл
                self.bot.execute_trading_cycle()
                
                # Показываем статистику каждые 5 минут
                elapsed = (time.time() - start_time) / 60
                if int(elapsed) % 5 == 0 and elapsed > 0:
                    self.print_statistics()
                
                # Ожидание перед следующим циклом
                time.sleep(60)  # 1 минута между циклами
            
            log_info("=" * 60)
            log_info("⏰ Время симуляции истекло")
            self.print_final_statistics()
            
        except KeyboardInterrupt:
            log_info("\n🛑 Симуляция остановлена пользователем")
            self.print_final_statistics()
    
    def print_statistics(self):
        """Вывод текущей статистики"""
        stats = self.simulator.get_statistics()
        current_profit = self.simulator.get_current_profit(
            self.bot.exchange.get_ticker(
                self.bot.settings.trading_pairs['active_pair']
            )['last']
        ) if self.simulator.position else None
        
        log_info("=" * 60)
        log_info("📊 ТЕКУЩАЯ СТАТИСТИКА")
        log_info("=" * 60)
        log_info(f"💰 Баланс: {self.simulator.balance:.2f} USDT")
        if current_profit:
            log_info(f"📈 Текущая прибыль: {current_profit['profit_percent']:.2f}% "
                   f"({current_profit['net_profit']:.2f} USDT)")
        log_info(f"📊 Всего сделок: {stats['total_trades']}")
        log_info(f"✅ Win Rate: {stats['win_rate']:.1f}%")
        log_info(f"📈 Общая прибыль: {stats['total_profit']:.2f} USDT "
               f"({stats['total_profit_percent']:.2f}%)")
        log_info("=" * 60)
    
    def print_final_statistics(self):
        """Вывод финальной статистики"""
        stats = self.simulator.get_statistics()
        
        log_info("=" * 60)
        log_info("📊 ФИНАЛЬНАЯ СТАТИСТИКА PAPER TRADING")
        log_info("=" * 60)
        log_info(f"💰 Начальный баланс: {stats['initial_balance']:.2f} USDT")
        log_info(f"💰 Конечный баланс: {stats['current_balance']:.2f} USDT")
        log_info(f"📈 Общая прибыль: {stats['total_profit']:.2f} USDT "
               f"({stats['total_profit_percent']:.2f}%)")
        log_info(f"📊 Всего сделок: {stats['total_trades']}")
        log_info(f"✅ Прибыльных: {stats['winning_trades']}")
        log_info(f"📊 Win Rate: {stats['win_rate']:.1f}%")
        log_info("=" * 60)
        
        # Сохранение результатов
        filename = f"paper_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'statistics': stats,
                'trades': self.simulator.trades
            }, f, indent=2, ensure_ascii=False)
        
        log_info(f"💾 Результаты сохранены в {filename}")


def main():
    """Главная функция"""
    print("=" * 60)
    print("🧪 PAPER TRADING - СИМУЛЯЦИЯ ТОРГОВЛИ")
    print("=" * 60)
    print()
    print("Этот режим позволяет тестировать стратегию в реальном времени")
    print("без реальных сделок на бирже.")
    print()
    
    initial_balance = input("Введите начальный баланс в USDT (по умолчанию 1000): ").strip()
    initial_balance = float(initial_balance) if initial_balance.replace('.', '').isdigit() else 1000.0
    
    duration = input("Введите продолжительность в минутах (по умолчанию 60): ").strip()
    duration = int(duration) if duration.isdigit() else 60
    
    print()
    print("=" * 60)
    print("🚀 Запуск Paper Trading...")
    print("=" * 60)
    print()
    
    paper_bot = PaperTradingBot(initial_balance=initial_balance)
    paper_bot.run(duration_minutes=duration)


if __name__ == "__main__":
    main()

