import { useQuery } from '@tanstack/react-query';
import { getStatus, getMarket } from '../services/api';
import StatusCard from '../components/StatusCard';
import MarketCard from '../components/MarketCard';

export default function Dashboard() {
  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['status'],
    queryFn: getStatus,
    refetchInterval: 5000, // Обновляем каждые 5 секунд
  });

  const { data: market, isLoading: marketLoading } = useQuery({
    queryKey: ['market'],
    queryFn: getMarket,
    refetchInterval: 2000, // Обновляем каждые 2 секунды
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-primary-400">
          KuCoin Trading Bot
        </h1>
        <p className="text-gray-400 mt-2">
          Node.js + TypeScript + React Dashboard
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <StatusCard data={status} isLoading={statusLoading} />
        <MarketCard data={market} isLoading={marketLoading} />
      </div>

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-2xl font-semibold mb-4">Управление</h2>
        <div className="flex gap-4">
          <button className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition">
            Запустить торговлю
          </button>
          <button className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold transition">
            Остановить торговлю
          </button>
        </div>
      </div>
    </div>
  );
}
