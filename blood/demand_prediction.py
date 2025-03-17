import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import holidays

class BloodDemandPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.scaler = StandardScaler()
        self.in_holidays = holidays.IN()  # Indian holidays

    def prepare_features(self, data):
        """Prepare features for prediction"""
        features = pd.DataFrame()
        
        # Time-based features
        features['month'] = data['demand_date'].dt.month
        features['day_of_week'] = data['demand_date'].dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Season feature
        features['season'] = self.get_season(data['demand_date'])
        
        # Holiday feature
        features['is_holiday'] = data['demand_date'].apply(
            lambda x: x in self.in_holidays).astype(int)
        
        # Hospital size feature (you might want to add this to Hospital model)
        features['hospital_size'] = data['hospital'].apply(
            lambda x: self.get_hospital_size(x))
        
        # Blood type features
        blood_type_dummies = pd.get_dummies(data['blood_type'], prefix='blood_type')
        features = pd.concat([features, blood_type_dummies], axis=1)
        
        # Emergency ratio feature
        features['emergency_ratio'] = data.groupby('hospital')['is_emergency'].transform('mean')
        
        return features

    def get_season(self, dates):
        """Convert dates to seasons"""
        return pd.Series(dates).apply(lambda x: (
            'Winter' if x.month in [12, 1, 2] else
            'Spring' if x.month in [3, 4, 5] else
            'Summer' if x.month in [6, 7, 8] else
            'Fall'
        ))

    def get_hospital_size(self, hospital):
        """Get hospital size score based on bed count or other metrics"""
        # You might want to add these fields to your Hospital model
        if hasattr(hospital, 'bed_count'):
            if hospital.bed_count > 500:
                return 3  # Large
            elif hospital.bed_count > 200:
                return 2  # Medium
            else:
                return 1  # Small
        return 2  # Default to medium if no bed count

    def train_model(self, historical_data):
        """Train the prediction model"""
        features = self.prepare_features(historical_data)
        target = historical_data['quantity']
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(features_scaled, target)

    def predict_demand(self, hospital, blood_type, prediction_date):
        """Predict blood demand for a specific date"""
        # Prepare prediction data
        pred_data = pd.DataFrame({
            'demand_date': [prediction_date],
            'hospital': [hospital],
            'blood_type': [blood_type],
            'is_emergency': [False]  # Default value
        })
        
        # Get features
        features = self.prepare_features(pred_data)
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.score(features_scaled, [prediction])
        
        return round(prediction), confidence

    def get_seasonal_pattern(self, historical_data):
        """Analyze seasonal patterns in blood demand"""
        seasonal_avg = historical_data.groupby(
            ['hospital', 'blood_type', 'season'])['quantity'].mean()
        return seasonal_avg

    def get_holiday_impact(self, historical_data):
        """Analyze impact of holidays on blood demand"""
        holiday_avg = historical_data.groupby(
            ['hospital', 'blood_type', 'is_holiday'])['quantity'].mean()
        return holiday_avg
