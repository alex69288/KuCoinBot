"""
ML МИКРОСЕРВИС ДЛЯ ТОРГОВОГО БОТА
Flask API для предсказаний ML модели
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Путь к моделям
MODEL_PATH = os.getenv('MODEL_PATH', '../ml_model.pkl')
SCALER_PATH = os.getenv('SCALER_PATH', '../scaler.pkl')

# Загрузка модели при старте
model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f"✅ ML модель загружена из {MODEL_PATH}")
    else:
        print(f"⚠️ ML модель не найдена в {MODEL_PATH}")
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Предсказание ML модели
    
    Ожидает JSON:
    {
        "features": [feature1, feature2, ...],
        "ohlcv": [[timestamp, open, high, low, close, volume], ...]
    }
    
    Возвращает:
    {
        "prediction": 0 or 1,
        "confidence": 0.0-1.0,
        "signal": "BUY" or "SELL" or "HOLD"
    }
    """
    if model is None or scaler is None:
        return jsonify({
            'error': 'ML model not loaded',
            'prediction': 0.5,
            'signal': 'HOLD'
        }), 503
    
    try:
        data = request.get_json()
        
        if 'features' not in data:
            return jsonify({'error': 'Missing features'}), 400
        
        features = np.array(data['features']).reshape(1, -1)
        
        # Масштабируем features
        features_scaled = scaler.transform(features)
        
        # Предсказание
        prediction = model.predict(features_scaled)[0]
        confidence = model.predict_proba(features_scaled)[0][prediction]
        
        # Определяем сигнал
        signal = 'HOLD'
        if prediction == 1 and confidence > 0.6:
            signal = 'BUY'
        elif prediction == 0 and confidence > 0.6:
            signal = 'SELL'
        
        return jsonify({
            'prediction': int(prediction),
            'confidence': float(confidence),
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/train', methods=['POST'])
def train():
    """
    Обучение модели (опционально)
    
    Ожидает JSON:
    {
        "ohlcv": [[timestamp, open, high, low, close, volume], ...],
        "epochs": 50
    }
    """
    # TODO: Реализовать обучение модели
    return jsonify({
        'message': 'Training not implemented yet'
    }), 501


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 ML Service starting on port {port}")
    print(f"📊 Model path: {MODEL_PATH}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
