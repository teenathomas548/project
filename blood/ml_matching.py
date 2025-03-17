import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

class MLMatchingSystem:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        # Initialize with some default data
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize the model with some default data"""
        # Create sample data for initial training
        sample_data = {
            
            'blood_compatibility': [1, 1, 0, 1, 0],
            'donor_age': [25, 35, 45, 30, 50],
            'days_since_donation': [100, 150, 95, 200, 120],
            'donor_points': [10, 20, 5, 15, 25],
            'is_emergency': [1, 0, 1, 0, 1],
            'quantity_needed': [2, 1, 3, 1, 2],
            'donor_active': [1, 1, 1, 1, 0]
        }
        
        # Create sample target (match success)
        sample_target = [1, 1, 0, 1, 0]
        
        # Fit the scaler and model
        X = pd.DataFrame(sample_data)
        y = np.array(sample_target)
        
        self.scaler.fit(X)
        self.model.fit(self.scaler.transform(X), y)

    def prepare_features(self, blood_request, donor):
        """Prepare features for ML model"""
        today = datetime.now().date()
        
        # Calculate donor age
        donor_age = (today - donor.date_of_birth).days // 365
        
        # Calculate days since last donation
        days_since_donation = 365  # Default if never donated
        if donor.last_donation_date:
            days_since_donation = (today - donor.last_donation_date).days

        features = {
            'blood_compatibility': self.get_blood_compatibility_score(
                donor.blood_type.blood_group,
                blood_request.blood_type.blood_group
            ),
            'donor_age': donor_age,
            'days_since_donation': days_since_donation,
            'donor_points': donor.points,
            'is_emergency': 1 if blood_request.urgency == 'emergency' else 0,
            'quantity_needed': blood_request.quantity,
            'donor_active': 1 if donor.is_active else 0
        }
        return pd.DataFrame([features])

    def get_blood_compatibility_score(self, donor_blood, recipient_blood):
        """Calculate blood compatibility score"""
        compatibility_matrix = {
            'O-': {'O-': 1, 'O+': 1, 'A-': 1, 'A+': 1, 'B-': 1, 'B+': 1, 'AB-': 1, 'AB+': 1},
            'O+': {'O+': 1, 'A+': 1, 'B+': 1, 'AB+': 1},
            'A-': {'A-': 1, 'A+': 1, 'AB-': 1, 'AB+': 1},
            'A+': {'A+': 1, 'AB+': 1},
            'B-': {'B-': 1, 'B+': 1, 'AB-': 1, 'AB+': 1},
            'B+': {'B+': 1, 'AB+': 1},
            'AB-': {'AB-': 1, 'AB+': 1},
            'AB+': {'AB+': 1}
        }
        return compatibility_matrix.get(donor_blood, {}).get(recipient_blood, 0)

    def predict_match_score(self, blood_request, donor):
        """Predict match score using ML model"""
        features = self.prepare_features(blood_request, donor)
        features_scaled = self.scaler.transform(features)
        return self.model.predict_proba(features_scaled)[0][1]