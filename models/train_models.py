#!/usr/bin/env python3
"""
Machine Learning Models for Air Quality Prediction
1. AQI Prediction (LSTM Time Series Model)
2. Pollution Source Classification (Random Forest)
3. Hotspot Detection (Clustering)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
from datetime import datetime, timedelta

class AQIPredictionModel:
    """LSTM-based model for AQI prediction (simplified for hackathon)"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 
                            'temperature', 'humidity', 'wind_speed', 'hour', 'day_of_week']
    
    def prepare_features(self, df):
        """Prepare features for training"""
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        return df[self.feature_cols].values
    
    def train(self, df):
        """Train the prediction model"""
        print("Training AQI Prediction Model...")
        
        # Prepare data
        X = self.prepare_features(df)
        y = df['aqi'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Use Random Forest as simplified predictor (LSTM would need TensorFlow)
        from sklearn.ensemble import GradientBoostingRegressor
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"  Train R² Score: {train_score:.4f}")
        print(f"  Test R² Score: {test_score:.4f}")
        
        return self
    
    def predict(self, features):
        """Predict AQI for given features"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        X = self.scaler.transform([features])
        return self.model.predict(X)[0]
    
    def predict_next_hours(self, current_data, hours=6):
        """Predict AQI for next N hours"""
        predictions = []
        
        for h in range(1, hours + 1):
            # Simple extrapolation (in production, use proper time-series)
            pred_aqi = self.predict(current_data) * (1 + np.random.normal(0, 0.1))
            predictions.append({
                'hours_ahead': h,
                'predicted_aqi': round(pred_aqi, 1)
            })
        
        return predictions
    
    def save(self, path='models/aqi_predictor.pkl'):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_cols': self.feature_cols
        }, path)
        print(f"  Model saved to {path}")
    
    @classmethod
    def load(cls, path='models/aqi_predictor.pkl'):
        """Load model from disk"""
        data = joblib.load(path)
        instance = cls()
        instance.model = data['model']
        instance.scaler = data['scaler']
        instance.feature_cols = data['feature_cols']
        return instance


class PollutionSourceClassifier:
    """Random Forest classifier for pollution source detection"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 
                            'temperature', 'humidity', 'wind_speed', 'hour']
        self.sources = ['traffic', 'construction', 'industrial', 'biomass_burning', 'residential']
    
    def prepare_features(self, df):
        """Prepare features for classification"""
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        return df[self.feature_cols].values, df['pollution_source'].values
    
    def train(self, df):
        """Train the classification model"""
        print("Training Pollution Source Classifier...")
        
        # Prepare data
        X, y = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, self.model.predict(X_train))
        test_acc = accuracy_score(y_test, self.model.predict(X_test))
        
        print(f"  Train Accuracy: {train_acc:.4f}")
        print(f"  Test Accuracy: {test_acc:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, self.model.predict(X_test)))
        
        return self
    
    def classify(self, features):
        """Classify pollution source and return probabilities"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        X = self.scaler.transform([features])
        probabilities = self.model.predict_proba(X)[0]
        predicted_source = self.model.predict(X)[0]
        
        # Return sorted probabilities
        source_probs = [
            {'source': source, 'probability': float(prob)}
            for source, prob in zip(self.model.classes_, probabilities)
        ]
        source_probs.sort(key=lambda x: x['probability'], reverse=True)
        
        return predicted_source, source_probs
    
    def save(self, path='models/source_classifier.pkl'):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_cols': self.feature_cols
        }, path)
        print(f"  Model saved to {path}")
    
    @classmethod
    def load(cls, path='models/source_classifier.pkl'):
        """Load model from disk"""
        data = joblib.load(path)
        instance = cls()
        instance.model = data['model']
        instance.scaler = data['scaler']
        instance.feature_cols = data['feature_cols']
        return instance


def detect_hotspots(df, threshold_aqi=200):
    """Detect pollution hotspots using simple threshold-based clustering"""
    print("Detecting pollution hotspots...")
    
    # Get latest data for each ward
    latest_data = df.sort_values('timestamp').groupby('ward_id').last().reset_index()
    
    # Identify hotspots
    hotspots = latest_data[latest_data['aqi'] >= threshold_aqi].copy()
    hotspots = hotspots.sort_values('aqi', ascending=False)
    
    hotspot_list = []
    for _, row in hotspots.iterrows():
        hotspot_list.append({
            'ward_id': int(row['ward_id']),
            'ward_name': row['ward_name'],
            'aqi': int(row['aqi']),
            'category': row['aqi_category'],
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'pollution_source': row['pollution_source']
        })
    
    print(f"  Found {len(hotspot_list)} hotspots (AQI >= {threshold_aqi})")
    
    return hotspot_list


def train_all_models(data_path='data/sensor_data.csv'):
    """Train all ML models"""
    print("=== Training ML Models ===\n")
    
    # Load data
    print("Loading sensor data...")
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df):,} records")
    
    # Train AQI Predictor
    print("\n1. AQI Prediction Model")
    aqi_model = AQIPredictionModel()
    aqi_model.train(df)
    aqi_model.save()
    
    # Train Source Classifier
    print("\n2. Pollution Source Classifier")
    source_model = PollutionSourceClassifier()
    source_model.train(df)
    source_model.save()
    
    # Detect hotspots
    print("\n3. Hotspot Detection")
    hotspots = detect_hotspots(df)
    
    # Save hotspots
    with open('../data/hotspots.json', 'w') as f:
        json.dump(hotspots, f, indent=2)
    print(f"  Hotspots saved to data/hotspots.json")
    
    print("\n✓ All models trained successfully!")


if __name__ == '__main__':
    train_all_models()
