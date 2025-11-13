# Shared Types

Общие TypeScript типы для Frontend и Backend.

## Использование

### В Backend (Node.js)

```typescript
import { BotStatus, MarketData, TradeSignal } from '../shared/types';

const status: BotStatus = {
  isRunning: true,
  tradingEnabled: false,
  // ...
};
```

### В Frontend (React)

```typescript
import type { BotStatus, MarketData } from '../shared/types';

interface Props {
  data: BotStatus;
}
```

## Типы

- **BotStatus** - статус бота и баланс
- **MarketData** - рыночные данные
- **TradeSignal** - торговый сигнал
- **Trade** - информация о сделке
- **BotSettings** - настройки бота
- **MLPrediction** - ML предсказание
- **Analytics** - аналитика и метрики

## Обновление

При изменении типов не забудьте:
1. Обновить Backend API
2. Обновить Frontend компоненты
3. Обновить ML Service типы (если нужно)
