# ML Service - Python ML Микросервис

Flask API для предсказаний ML модели торгового бота.

## 🚀 Быстрый Старт

### 1. Установка зависимостей

```bash
cd ml-service
pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

### 3. Запуск

**Development режим**:
```bash
python app.py
```

**Production режим** (с gunicorn):
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

## 🔌 API Endpoints

### Health Check
```http
GET /health

Response:
{
  "status": "ok",
  "model_loaded": true,
  "timestamp": "2025-11-13T..."
}
```

### Predict
```http
POST /predict

Body:
{
  "features": [0.5, 0.3, 0.7, ...],
  "ohlcv": [[timestamp, open, high, low, close, volume], ...]
}

Response:
{
  "prediction": 1,
  "confidence": 0.85,
  "signal": "BUY",
  "timestamp": "2025-11-13T..."
}
```

## 🐳 Docker

Собрать образ:
```bash
docker build -t ml-service .
```

Запустить:
```bash
docker run -p 5000:5000 --env-file .env ml-service
```

## 📝 TODO

- [ ] Портировать текущую ML модель из Python бота
- [ ] Добавить endpoint для обучения модели
- [ ] Реализовать feature engineering
- [ ] Добавить кеширование предсказаний
- [ ] Логирование в файл
- [ ] Метрики для мониторинга
