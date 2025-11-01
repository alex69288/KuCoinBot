"""
ML МОДЕЛЬ И ОБУЧЕНИЕ (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ) - ИСПРАВЛЕННЫЙ ВЫВОД
"""
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from .features import FeatureEngineer

class MLModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_engineer = FeatureEngineer()
        self.is_trained = False
        
    def load_model(self):
        """Загрузка модели"""
        try:
            if joblib.os.path.exists('ml_model.pkl') and joblib.os.path.exists('scaler.pkl'):
                self.model = joblib.load('ml_model.pkl')
                self.scaler = joblib.load('scaler.pkl')
                self.is_trained = True
                print("✅ ML-модель загружена из кэша")
                return True
            else:
                print("⚠️ ML-модель не найдена, требуется обучение")
                return False
        except Exception as e:
            print(f"❌ Ошибка загрузки ML: {e}")
            return False

    def train(self, exchange, symbol='BTC/USDT', timeframe='1h', limit=80):
        """ОБЛЕГЧЕННОЕ обучение модели для быстрого старта"""
        try:
            # Используем МЕНЬШЕ данных для быстрого старта
            print(f"🤖 Быстрое обучение ML на {limit} свечах...")
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if len(ohlcv) < 40:  # Уменьшили минимальное количество
                print("⚠️ Недостаточно данных для быстрого обучения ML")
                return False
            
            X = []
            y = []
            
            # Упрощенная подготовка данных
            for i in range(20, len(ohlcv) - 1):  # Меньше данных для обучения
                features = self.feature_engineer.prepare_features(ohlcv[:i+1])
                if features:
                    future_price = ohlcv[i+1][4]
                    current_price = ohlcv[i][4]
                    target = 1 if future_price > current_price else 0
                    
                    X.append(features)
                    y.append(target)
            
            if len(X) < 25:  # Уменьшили порог
                print("⚠️ Недостаточно данных для быстрого обучения")
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # УПРОЩЕННАЯ МОДЕЛЬ для быстрого обучения
            self.model = RandomForestClassifier(
                n_estimators=50,  # Меньше деревьев
                max_depth=8,      # Меньшая глубина
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1
            )
            
            # Обучение БЕЗ разделения на тест/трейд для скорости
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Быстрая оценка
            train_score = self.model.score(X_scaled, y)
            
            print(f"✅ ML-модель обучена (быстрый режим)")
            print(f"   Точность на обучающих данных: {train_score:.3f}")
            
            # Сохраняем модель
            joblib.dump(self.model, 'ml_model.pkl')
            joblib.dump(self.scaler, 'scaler.pkl')
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка быстрого обучения ML: {e}")
            return False

    def predict(self, ohlcv_data):
        """Предсказание на новых данных - ИСПРАВЛЕННЫЙ ВЫВОД"""
        if not self.is_trained or self.model is None:
            return 0.5, "⚪ ML НЕ ОБУЧЕН"
        
        try:
            features = self.feature_engineer.prepare_features(ohlcv_data)
            if not features:
                return 0.5, "⚠️ НЕДОСТАТОЧНО ДАННЫХ"
            
            features_scaled = self.scaler.transform([features])
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            confidence = prediction_proba[1]  # Вероятность роста
            
            # ИСПРАВЛЕННАЯ ИНТЕРПРЕТАЦИЯ УВЕРЕННОСТИ
            if confidence > 0.7:
                signal = "🟢 СИЛЬНЫЙ РОСТ"
            elif confidence > 0.6:
                signal = "🟡 УМЕРЕННЫЙ РОСТ" 
            elif confidence > 0.5:
                signal = "⚪ НЕЙТРАЛЬНО"
            elif confidence > 0.4:
                signal = "🟡 УМЕРЕННОЕ ПАДЕНИЕ"
            else:
                signal = "🔴 СИЛЬНОЕ ПАДЕНИЕ"
            
            return confidence, signal
            
        except Exception as e:
            print(f"❌ Ошибка предсказания ML: {e}")
            return 0.5, "❌ ОШИБКА ПРЕДСКАЗАНИЯ"

    def get_feature_importance(self):
        """Важность фич"""
        if not self.is_trained or self.model is None:
            return {}
        
        try:
            feature_names = self.feature_engineer.get_feature_names()
            importances = self.model.feature_importances_
            
            # Сортируем по важности
            feature_importance = dict(zip(feature_names, importances))
            sorted_importance = dict(sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            return sorted_importance
        except:
            return {}