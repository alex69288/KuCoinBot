"""
МЕТРИКИ И СТАТИСТИКА
"""
from datetime import datetime, timedelta
from utils.logger import log_info

class AnalyticsMetrics:
    def __init__(self):
        self.reset_metrics()
    
    def reset_metrics(self):
        """Сброс метрик"""
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_profit_usdt = 0.0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.best_trade = 0.0
        self.worst_trade = 0.0
        self.best_trade_usdt = 0.0
        self.worst_trade_usdt = 0.0
        self.average_win = 0.0
        self.average_loss = 0.0
        self.average_win_usdt = 0.0
        self.average_loss_usdt = 0.0
        self.win_rate = 0.0
        self.profit_factor = 0.0
        self.sharpe_ratio = 0.0
        self.trade_history = []
        self.daily_performance = {}
        self.weekly_performance = {}
        
        self.peak_equity = 0.0
        self.current_equity = 10000.0  # Начальный капитал для расчета просадки
        self.daily_profit = 0.0
        self.daily_profit_usdt = 0.0
        self.last_reset_date = datetime.now().date()
    
    def get_current_time(self):
        """Получение текущего времени"""
        return datetime.now().strftime("%H:%M:%S")
    
    def update_metrics(self, trade_result):
        """Обновление метрик после сделки с USDT"""
        try:
            self.total_trades += 1
            profit = trade_result.get('profit', 0)
            profit_percent = trade_result.get('profit_percent', 0)
            profit_usdt = trade_result.get('profit_usdt', 0)
            position_size_usdt = trade_result.get('position_size_usdt', 0)
            
            # Обновляем общую прибыль в процентах и USDT
            self.total_profit += profit
            self.total_profit_usdt += profit_usdt
            
            # Обновляем счетчики побед/поражений
            if profit > 0:
                self.winning_trades += 1
                self.consecutive_wins += 1
                self.consecutive_losses = 0
            else:
                self.losing_trades += 1
                self.consecutive_losses += 1
                self.consecutive_wins = 0
            
            # Обновляем лучшую/худшую сделку в процентах
            if profit > self.best_trade:
                self.best_trade = profit
            if profit < self.worst_trade:
                self.worst_trade = profit
            
            # Обновляем лучшую/худшую сделку в USDT
            if profit_usdt > self.best_trade_usdt:
                self.best_trade_usdt = profit_usdt
            if profit_usdt < self.worst_trade_usdt:
                self.worst_trade_usdt = profit_usdt
            
            # Пересчитываем средние значения в процентах
            if self.winning_trades > 0:
                self.average_win = self.total_profit / self.winning_trades
            if self.losing_trades > 0:
                self.average_loss = abs(self.total_profit) / self.losing_trades
            
            # Пересчитываем средние значения в USDT
            if self.winning_trades > 0:
                self.average_win_usdt = self.total_profit_usdt / self.winning_trades
            if self.losing_trades > 0:
                self.average_loss_usdt = abs(self.total_profit_usdt) / self.losing_trades
            
            # Расчет Win Rate
            if self.total_trades > 0:
                self.win_rate = (self.winning_trades / self.total_trades) * 100
            
            # Расчет Profit Factor
            if self.average_loss > 0:
                self.profit_factor = self.average_win / self.average_loss
            
            # Обновляем просадку
            self.current_equity += profit
            if self.current_equity > self.peak_equity:
                self.peak_equity = self.current_equity
            
            # ИСПРАВЛЕННАЯ СТРОКА - правильный синтаксис тернарного оператора
            if self.peak_equity > 0:
                drawdown = ((self.peak_equity - self.current_equity) / self.peak_equity * 100)
            else:
                drawdown = 0
            
            self.current_drawdown = drawdown
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
            
            # Добавляем в историю с USDT
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': trade_result.get('symbol', ''),
                'signal': trade_result.get('signal', ''),
                'profit': profit,
                'profit_percent': profit_percent,
                'profit_usdt': profit_usdt,
                'position_size_usdt': position_size_usdt,
                'price': trade_result.get('price', 0),
                'position_size': trade_result.get('position_size', 0)
            }
            self.trade_history.append(trade_record)
            
            # Обновляем дневную статистику
            today = datetime.now().date()
            if today not in self.daily_performance:
                self.daily_performance[today] = {
                    'trades': 0,
                    'profit': 0.0,
                    'profit_usdt': 0.0,
                    'winning_trades': 0,
                    'losing_trades': 0
                }
            
            self.daily_performance[today]['trades'] += 1
            self.daily_performance[today]['profit'] += profit
            self.daily_performance[today]['profit_usdt'] += profit_usdt
            if profit > 0:
                self.daily_performance[today]['winning_trades'] += 1
            else:
                self.daily_performance[today]['losing_trades'] += 1
            
            log_info(f"📊 Метрики обновлены: сделок {self.total_trades}, "
                    f"Win Rate {self.win_rate:.1f}%, прибыль {self.total_profit:.2f}% ({self.total_profit_usdt:.2f} USDT)")
                    
        except Exception as e:
            log_info(f"❌ Ошибка обновления метрик: {e}")
    
    def get_summary(self):
        """Получение сводки метрик"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_profit': self.total_profit,
            'total_profit_usdt': self.total_profit_usdt,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown,
            'best_trade': self.best_trade,
            'worst_trade': self.worst_trade,
            'best_trade_usdt': self.best_trade_usdt,
            'worst_trade_usdt': self.worst_trade_usdt,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'average_win_usdt': self.average_win_usdt,
            'average_loss_usdt': self.average_loss_usdt,
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses
        }
    
    def get_performance_report(self, period='all'):
        """Отчет о производительности с USDT"""
        summary = self.get_summary()
        
        report = f"""
📊 <b>АНАЛИТИКА ТОРГОВЛИ</b>

📈 <b>ОСНОВНЫЕ МЕТРИКИ:</b>
• Всего сделок: <b>{summary['total_trades']}</b>
• Win Rate: <b>{summary['win_rate']:.1f}%</b>
• Profit Factor: <b>{summary['profit_factor']:.2f}</b>
• Общая прибыль: <b>{summary['total_profit']:.2f}% ({summary['total_profit_usdt']:.2f} USDT)</b>

💰 <b>СТАТИСТИКА СДЕЛОК:</b>
• Прибыльных: <b>{summary['winning_trades']}</b>
• Убыточных: <b>{summary['losing_trades']}</b>
• Средняя прибыль: <b>{summary['average_win']:.2f}% ({summary['average_win_usdt']:.2f} USDT)</b>
• Средний убыток: <b>{summary['average_loss']:.2f}% ({summary['average_loss_usdt']:.2f} USDT)</b>

🎯 <b>РЕКОРДЫ:</b>
• Лучшая сделка: <b>{summary['best_trade']:.2f}% ({summary['best_trade_usdt']:.2f} USDT)</b>
• Худшая сделка: <b>{summary['worst_trade']:.2f}% ({summary['worst_trade_usdt']:.2f} USDT)</b>
• Серия побед: <b>{summary['consecutive_wins']}</b>
• Серия поражений: <b>{summary['consecutive_losses']}</b>

⚡ <b>РИСКИ:</b>
• Макс просадка: <b>{summary['max_drawdown']:.2f}%</b>
• Текущая просадка: <b>{summary['current_drawdown']:.2f}%</b>
"""
        return report
    
    def get_daily_summary(self):
        """Сводка за сегодня"""
        today = datetime.now().date()
        daily_data = self.daily_performance.get(today, {})
        
        trades_today = daily_data.get('trades', 0)
        profit_today = daily_data.get('profit', 0)
        profit_usdt_today = daily_data.get('profit_usdt', 0)
        winning_trades_today = daily_data.get('winning_trades', 0)
        losing_trades_today = daily_data.get('losing_trades', 0)
        
        win_rate_today = (winning_trades_today / trades_today * 100) if trades_today > 0 else 0
        
        return {
            'date': today,
            'trades': trades_today,
            'profit': profit_today,
            'profit_usdt': profit_usdt_today,
            'winning_trades': winning_trades_today,
            'losing_trades': losing_trades_today,
            'win_rate': win_rate_today
        }
    
    def get_trade_history_formatted(self, limit=10):
        """Форматированная история сделок"""
        if not self.trade_history:
            return "История сделок пуста"
        
        recent_trades = self.trade_history[-limit:]
        formatted = []
        
        for trade in recent_trades:
            emoji = "🟢" if trade['profit'] > 0 else "🔴"
            profit_str = f"+{trade['profit']:.2f}%" if trade['profit'] > 0 else f"{trade['profit']:.2f}%"
            profit_usdt_str = f"+{trade['profit_usdt']:.2f} USDT" if trade['profit_usdt'] > 0 else f"{trade['profit_usdt']:.2f} USDT"
            
            formatted.append(
                f"{emoji} {trade['signal'].upper()} {trade['symbol']} - "
                f"{trade['price']:.2f} USDT ({profit_str} / {profit_usdt_str})"
            )
        
        return "\n".join(formatted)
    
    def get_position_statistics(self):
        """Статистика по открытым позициям"""
        if not self.trade_history:
            return None
        
        # Находим открытые позиции (последняя сделка - покупка без продажи)
        open_positions = []
        for trade in reversed(self.trade_history):
            if trade['signal'] == 'buy':
                # Проверяем, была ли продажа после этой покупки
                has_sell = any(
                    t for t in self.trade_history 
                    if t['timestamp'] > trade['timestamp'] and t['signal'] == 'sell'
                )
                if not has_sell:
                    open_positions.append(trade)
        
        return {
            'open_positions': len(open_positions),
            'total_invested': sum(pos['position_size_usdt'] for pos in open_positions),
            'positions': open_positions
        }
    
    def cleanup_old_data(self, days_to_keep=30):
        """Очистка старых данных"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Очищаем историю сделок
            self.trade_history = [
                trade for trade in self.trade_history 
                if trade['timestamp'] > cutoff_date
            ]
            
            # Очищаем дневную статистику
            self.daily_performance = {
                date: data for date, data in self.daily_performance.items()
                if date > cutoff_date.date()
            }
            
            log_info(f"🧹 Очищены данные старше {days_to_keep} дней")
            
        except Exception as e:
            log_info(f"❌ Ошибка очистки данных: {e}")
    
    def calculate_roi(self, initial_capital=10000):
        """Расчет ROI"""
        if initial_capital > 0:
            return (self.total_profit_usdt / initial_capital) * 100
        return 0
    
    def get_risk_metrics(self):
        """Метрики риска"""
        if self.total_trades == 0:
            return {}
        
        # Расчет Sharpe Ratio (упрощенный)
        returns = [trade['profit'] for trade in self.trade_history]
        avg_return = sum(returns) / len(returns)
        std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        
        sharpe_ratio = avg_return / std_dev if std_dev > 0 else 0
        
        # Расчет максимальной просадки в USDT
        equity_curve = []
        current_equity = 10000  # Начальный капитал
        for trade in self.trade_history:
            current_equity += trade['profit_usdt']
            equity_curve.append(current_equity)
        
        max_drawdown_usdt = 0
        peak = equity_curve[0] if equity_curve else 0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_drawdown_usdt:
                max_drawdown_usdt = drawdown
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'volatility': std_dev,
            'max_drawdown_usdt': max_drawdown_usdt,
            'avg_trade_return': avg_return,
            'expectancy': (self.win_rate/100 * self.average_win + 
                          (1 - self.win_rate/100) * self.average_loss)
        }