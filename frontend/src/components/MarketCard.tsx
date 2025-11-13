import { MarketData } from '../services/api';

interface MarketCardProps {
  data?: MarketData;
  isLoading: boolean;
}

export default function MarketCard({ data, isLoading }: MarketCardProps) {
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
        Рынок
      </h2>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">Пара:</span>
          <span className="font-semibold text-white text-lg">
            {data.symbol}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Цена:</span>
          <span className="font-bold text-2xl text-primary-400">
            ${data.price.toLocaleString()}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Изменение 24ч:</span>
          <span className={`font-semibold ${data.change24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data.change24h >= 0 ? '+' : ''}{data.change24h.toFixed(2)}%
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Max 24ч:</span>
          <span className="text-white">
            ${data.high24h.toLocaleString()}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Min 24ч:</span>
          <span className="text-white">
            ${data.low24h.toLocaleString()}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-400">Объем:</span>
          <span className="text-white">
            ${(data.volume / 1000000).toFixed(2)}M
          </span>
        </div>
      </div>
    </div>
  );
}
