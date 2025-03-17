import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

class IronPredictionModel:
    def __init__(self):
        self.model = None
        self.model_path = 'blood/ml_models/iron_prediction_model.joblib'

    def load_and_train_model(self):
        try:
            # Check if trained model exists
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                return True

            # Create training data from existing BloodTest records
            from .models import BloodTest
            blood_tests = BloodTest.objects.all().values(
                'hemoglobin',
                'donation__donor__blood_type',
                'donation__donor__date_of_birth'
            )
            
            if not blood_tests:
                # If no data, create a simple model based on WHO guidelines
                # This ensures the model works even without historical data
                X = np.array([[7.0], [10.0], [13.0], [15.0]])
                y = np.array(['severe', 'moderate', 'mild', 'normal'])
                
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.model.fit(X, y)
                
                # Save model
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                joblib.dump(self.model, self.model_path)
                return True
            
            df = pd.DataFrame(blood_tests)
            
            # Prepare features
            X = df[['hemoglobin']]
            
            # Create target based on WHO guidelines
            def get_severity(hemoglobin):
                hb = float(hemoglobin)
                if hb < 7:
                    return 'severe'
                elif hb < 10:
                    return 'moderate'
                elif hb < 13:
                    return 'mild'
                return 'normal'
            
            y = df['hemoglobin'].apply(get_severity)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X, y)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            
            return True
            
        except Exception as e:
            print(f"Error in model training: {e}")
            return False

    def predict_iron_status(self, hemoglobin):
        try:
            if not self.model:
                success = self.load_and_train_model()
                if not success:
                    return {
                        'severity': self.get_severity_without_model(hemoglobin),
                        'confidence': 100  # Using WHO guidelines directly
                    }
            
            features = np.array([[float(hemoglobin)]])
            severity = self.model.predict(features)[0]
            probability = np.max(self.model.predict_proba(features))
            
            return {
                'severity': severity,
                'confidence': round(probability * 100, 2)
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return {
                'severity': self.get_severity_without_model(hemoglobin),
                'confidence': 100  # Using WHO guidelines directly
            }

    def get_severity_without_model(self, hemoglobin):
        """Fallback method using WHO guidelines"""
        hb = float(hemoglobin)
        if hb < 7:
            return 'severe'
        elif hb < 10:
            return 'moderate'
        elif hb < 13:
            return 'mild'
        return 'normal'