# blood/donor_prediction.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
from .models import DonorProfile

class DonorAvailabilityPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def prepare_features(self, donor):
        today = datetime.now().date()
        
        # Calculate days since last donation
        days_since_last_donation = (today - donor.last_donation_date).days if donor.last_donation_date else 365
        
        # Calculate age
        age = (today - donor.date_of_birth).days // 365
        
        features = {
            'age': age,
            'days_since_last_donation': days_since_last_donation,
            'total_donations': donor.points,  # Assuming points represent total donations
            'is_active': 1 if donor.is_active else 0
        }
        
        return features
        
    def train_model(self):
        donors = DonorProfile.objects.all()
        features_list = []
        targets = []
        
        for donor in donors:
            features = self.prepare_features(donor)
            features_list.append(features)
            targets.append(donor.is_active)  # Assuming availability is linked to is_active
            
        # Convert to DataFrame
        X = pd.DataFrame(features_list)
        y = np.array(targets)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train the model
        self.model.fit(X_train_scaled, y_train)
        
        # Return test accuracy
        return self.model.score(X_test_scaled, y_test)
        
    def predict_availability(self, donor):
        features = self.prepare_features(donor)
        features_df = pd.DataFrame([features])
        features_scaled = self.scaler.transform(features_df)
        
        # Get probability of availability
        probability = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            'is_available': self.model.predict(features_scaled)[0],
            'probability': probability
        }