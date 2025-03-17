import numpy as np
from sklearn.ensemble import RandomForestClassifier

class IronStatusPredictor:
    def __init__(self):
        self.model = self.train_model()

    def generate_synthetic_data(self, n_samples=1000):  # Increased samples
        """Generate synthetic training data"""
        np.random.seed(42)
        
        # Generate synthetic features
        X = np.random.rand(n_samples, 5)
        X[:, 0] = X[:, 0] * 5 + 10  # Hemoglobin (10-15)
        X[:, 1] = X[:, 1] * 195 + 5  # Ferritin (5-200)
        X[:, 2] = X[:, 2] * 0.9 + 0.1  # TSI (0.1-1.0)
        X[:, 3] = X[:, 3] * 300 + 100  # TIBC (100-400)
        X[:, 4] = np.random.randint(0, 6, n_samples)  # Donations

        # Generate labels based on medical criteria
        y = []
        for i in range(n_samples):
            if X[i, 1] < 30 or X[i, 2] < 0.2:  # Low ferritin or low TSI
                if X[i, 0] < 12:  # Low hemoglobin
                    y.append('Iron Deficiency Anemia')
                else:
                    y.append('Iron Deficiency')
            else:
                y.append('Normal')
        
        return X, np.array(y)

    def train_model(self):
        X, y = self.generate_synthetic_data()
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model

    def predict(self, features):
        features_array = np.array(features).reshape(1, -1)
        return self.model.predict(features_array)[0]

    def get_diet_recommendation(self, iron_status):
        recommendations = {
            'Normal': 'Maintain a balanced diet rich in iron. Include lean meats, fish, and green leafy vegetables.',
            'Iron Deficiency': 'Increase iron intake through red meat, spinach, legumes, and fortified cereals. Consider iron supplements.',
            'Iron Deficiency Anemia': 'Urgent dietary changes needed: Include high-iron foods, vitamin C supplements, and consult healthcare provider.'
        }
        return recommendations.get(iron_status, 'Please consult with your healthcare provider for personalized dietary advice.')
