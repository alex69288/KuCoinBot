"""
ГЕНЕРАЦИЯ ОТЧЕТОВ И АНАЛИТИКИ
"""
from datetime import datetime, timedelta
from utils.logger import log_info

class ReportGenerator:
    def __init__(self, metrics_manager):
        self.metrics = metrics_manager
    
    def generate_performance_report(self, period='all'):
        """Генерация отчета о производительности"""
        summary = self.metrics.get_summary()
        
        report = f"""
📊 <b>ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ</b>
⏰ Период: {self._get_period_name(period)}

📈 <b>ОСНОВНЫЕ МЕТРИКИ:</b>
• Всего сделок: <b>{summary['total_trades']}</b>
• Win Rate: <b>{summary['win_rate']:.1f}%</b>
• Profit Factor: <b>{summary['profit_factor']:.2f}</b>
• Общая прибыль: <b>{summary['total_profit']:.2f} USDT</b>
• Макс просадка: <b>{summary['max_drawdown']:.2f}%</b>

💰 <b>СТАТИСТИКА СДЕЛОК:</b>
• Прибыльных: <b>{summary['winning_trades']}</b>
• Убыточных: <b>{summary['losing_trades']}</b>
• Средняя прибыль: <b>{summary['average_win']:.2f} USDT</b>
• Средний убыток: <b>{summary['average_loss']:.2f} USDT</b>
• Соотношение прибыль/убыток: <b>{summary['average_win']/abs(summary['average_loss']):.2f}</b>

🎯 <b>РЕКОРДЫ И СЕРИИ:</b>
• Лучшая сделка: <b>{summary['best_trade']:.2f} USDT</b>
• Худшая сделка: <b>{summary['worst_trade']:.2f} USDT</b>
• Серия побед: <b>{summary['consecutive_wins']}</b>
• Серия поражений: <b>{summary['consecutive_losses']}</b>

⚡ <b>ЭФФЕКТИВНОСТЬ:</b>
• Sharpe Ratio: <b>{summary.get('sharpe_ratio', 0):.2f}</b>
• Expectancy: <b>{self._calculate_expectancy(summary):.2f} USDT</b>
• ROI: <b>{self._calculate_roi(summary):.2f}%</b>
"""
        return report
    
    def generate_daily_report(self):
        """Генерация дневного отчета"""
        today = datetime.now().date()
        daily_data = self.metrics.daily_performance.get(today, {})
        
        trades_today = daily_data.get('trades', 0)
        profit_today = daily_data.get('profit', 0)
        winning_trades_today = daily_data.get('winning_trades', 0)
        losing_trades_today = daily_data.get('losing_trades', 0)
        
        win_rate_today = (winning_trades_today / trades_today * 100) if trades_today > 0 else 0
        
        report = f"""
📅 <b>ДНЕВНОЙ ОТЧЕТ</b>
⏰ Дата: {today.strftime('%d.%m.%Y')}

📊 <b>СЕГОДНЯ:</b>
• Сделок: <b>{trades_today}</b>
• Прибыль: <b>{profit_today:+.2f} USDT</b>
• Win Rate: <b>{win_rate_today:.1f}%</b>
• Прибыльных: <b>{winning_trades_today}</b>
• Убыточных: <b>{losing_trades_today}</b>

📈 <b>ОБЩАЯ СТАТИСТИКА:</b>
• Всего сделок: <b>{self.metrics.total_trades}</b>
• Общая прибыль: <b>{self.metrics.total_profit:.2f} USDT</b>
• Win Rate: <b>{self.metrics.win_rate:.1f}%</b>
• Profit Factor: <b>{self.metrics.profit_factor:.2f}</b>

🎯 <b>РЕКОМЕНДАЦИИ:</b>
{self._generate_recommendations()}
"""
        return report
    
    def generate_strategy_comparison(self, strategy_performance):
        """Генерация сравнения стратегий"""
        if not strategy_performance:
            return "📊 <b>СРАВНЕНИЕ СТРАТЕГИЙ</b>\n\nНет данных для сравнения"
        
        report = "📊 <b>СРАВНЕНИЕ СТРАТЕГИЙ</b>\n\n"
        
        for strategy, stats in strategy_performance.items():
            report += f"""
🎯 <b>{strategy}</b>
• Сделок: <b>{stats.get('trades', 0)}</b>
• Win Rate: <b>{stats.get('win_rate', 0):.1f}%</b>
• Прибыль: <b>{stats.get('profit', 0):.2f} USDT</b>
• Profit Factor: <b>{stats.get('profit_factor', 0):.2f}</b>
• Макс просадка: <b>{stats.get('max_drawdown', 0):.2f}%</b>
────────────────────
"""
        return report
    
    def generate_risk_report(self, risk_manager):
        """Генерация отчета по рискам"""
        risk_summary = risk_manager.get_risk_summary()
        
        report = f"""
⚡ <b>ОТЧЕТ ПО РИСКАМ</b>

📊 <b>ТЕКУЩИЕ РИСКИ:</b>
• Дневные убытки: <b>{risk_summary['daily_losses']:.2f}%</b>
• Макс допустимо: <b>{risk_summary['max_daily_loss']:.2f}%</b>
• Серия убытков: <b>{risk_summary['consecutive_losses']}</b>
• Макс допустимо: <b>{risk_summary['max_consecutive_losses']}</b>
• Сделок сегодня: <b>{risk_summary['trades_today']}</b>

🎯 <b>СТАТУС ТОРГОВЛИ:</b>
• Торговля разрешена: <b>{'✅ ДА' if risk_manager.can_trade() else '❌ НЕТ'}</b>
• Уровень риска: <b>{self._calculate_risk_level(risk_summary)}</b>

💡 <b>РЕКОМЕНДАЦИИ:</b>
{self._generate_risk_recommendations(risk_summary)}
"""
        return report
    
    def generate_ml_report(self, ml_model):
        """Генерация отчета по ML модели"""
        feature_importance = ml_model.get_feature_importance()
        
        report = f"""
🤖 <b>ОТЧЕТ ПО ML МОДЕЛИ</b>

📊 <b>СТАТУС МОДЕЛИ:</b>
• Обучена: <b>{'✅ ДА' if ml_model.is_trained else '❌ НЕТ'}</b>
• Количество фич: <b>{len(feature_importance)}</b>

🎯 <b>ВАЖНОСТЬ ФИЧ (ТОП-5):</b>
"""
        
        if feature_importance:
            top_features = list(feature_importance.items())[:5]
            for i, (feature, importance) in enumerate(top_features, 1):
                report += f"{i}. {feature}: <b>{importance:.3f}</b>\n"
        else:
            report += "Нет данных о важности фич\n"
        
        report += f"""
📈 <b>РЕКОМЕНДАЦИИ:</b>
• Используйте модель для фильтрации сигналов
• Настройте пороги уверенности
• Регулярно переобучайте модель
"""
        return report
    
    def _get_period_name(self, period):
        """Получение названия периода"""
        periods = {
            'all': 'Всё время',
            'week': 'Неделя',
            'month': 'Месяц',
            'year': 'Год'
        }
        return periods.get(period, 'Всё время')
    
    def _calculate_expectancy(self, summary):
        """Расчет математического ожидания"""
        if summary['total_trades'] == 0:
            return 0
        return (summary['win_rate']/100 * summary['average_win'] + 
                (1 - summary['win_rate']/100) * summary['average_loss'])
    
    def _calculate_roi(self, summary):
        """Расчет ROI"""
        if summary['total_trades'] == 0:
            return 0
        return (summary['total_profit'] / summary['total_trades'])
    
    def _calculate_risk_level(self, risk_summary):
        """Расчет уровня риска"""
        daily_risk = risk_summary['daily_losses'] / risk_summary['max_daily_loss']
        consecutive_risk = risk_summary['consecutive_losses'] / risk_summary['max_consecutive_losses']
        
        max_risk = max(daily_risk, consecutive_risk)
        
        if max_risk < 0.3:
            return "🟢 НИЗКИЙ"
        elif max_risk < 0.7:
            return "🟡 СРЕДНИЙ"
        else:
            return "🔴 ВЫСОКИЙ"
    
    def _generate_recommendations(self):
        """Генерация рекомендаций на основе статистики"""
        recommendations = []
        
        if self.metrics.total_trades < 10:
            recommendations.append("• Накопите больше статистики перед анализом")
        
        if self.metrics.win_rate < 40:
            recommendations.append("• Рассмотрите изменение стратегии")
        elif self.metrics.win_rate > 60:
            recommendations.append("• Отличные результаты! Продолжайте в том же духе")
        
        if self.metrics.profit_factor < 1.0:
            recommendations.append("• Увеличьте соотношение прибыль/убыток")
        
        if self.metrics.max_drawdown > 10:
            recommendations.append("• Уменьшите максимальную просадку")
        
        if not recommendations:
            recommendations.append("• Статистика в норме, продолжайте торговлю")
        
        return "\n".join(recommendations)
    
    def _generate_risk_recommendations(self, risk_summary):
        """Генерация рекомендаций по рискам"""
        recommendations = []
        
        if risk_summary['daily_losses'] > risk_summary['max_daily_loss'] * 0.8:
            recommendations.append("• Близко к дневному лимиту потерь")
        
        if risk_summary['consecutive_losses'] > risk_summary['max_consecutive_losses'] * 0.8:
            recommendations.append("• Близко к лимиту убыточных сделок подряд")
        
        if risk_summary['trades_today'] > 10:
            recommendations.append("• Много сделок сегодня, будьте осторожны")
        
        if not recommendations:
            recommendations.append("• Риски под контролем")
        
        return "\n".join(recommendations)