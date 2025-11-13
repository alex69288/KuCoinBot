import type { BotStatus } from '../services/api';

interface StatusCardProps {
  data?: BotStatus;
  isLoading: boolean;
}

export default function StatusCard({ data, isLoading }: StatusCardProps) {
  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 animate-pulse">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-700 rounded"></div>
          <div className="h-4 bg-gray-700 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-semibold mb-4 text-primary-400">
        Статус Бота
      </h2>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Статус:</span>
          <span className={`font-semibold ${data.isRunning ? 'text-green-400' : 'text-red-400'}`}>
            {data.isRunning ? '🟢 Работает' : '🔴 Остановлен'}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Торговля:</span>
          <span className={`font-semibold ${data.tradingEnabled ? 'text-green-400' : 'text-yellow-400'}`}>
            {data.tradingEnabled ? '✅ Включена' : '⚠️ Отключена'}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Баланс:</span>
          <span className="font-semibold text-white">
            ${data.balance.available.toFixed(2)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Позиций:</span>
          <span className="font-semibold text-white">
            {data.positions.total}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Прибыль:</span>
          <span className={`font-semibold ${data.positions.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.positions.profit >= 0 ? '+' : ''}${data.positions.profit.toFixed(2)}
          </span>
        </div>

        <div className="flex justify-between items-center text-sm pt-3 border-t border-gray-700">
          <span className="text-gray-500">Uptime:</span>
          <span className="text-gray-400">
            {Math.floor(data.uptime / 60)} мин
          </span>
        </div>
      </div>
    </div>
  );
}
