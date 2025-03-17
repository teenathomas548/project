class DietRecommendationEngine:
    def __init__(self):
        self.diet_recommendations = {
            'severe': {
                'vegetarian': [
                    'Iron-fortified cereals',
                    'Spinach and leafy greens',
                    'Legumes and lentils',
                    'Dried fruits',
                    'Vitamin C rich fruits'
                ],
                'non_vegetarian': [
                    'Lean red meat',
                    'Organ meats',
                    'Fish',
                    'Eggs',
                    'Green vegetables'
                ]
            },
            # ... similar structures for 'moderate', 'mild', 'normal'
        }
        
        self.supplements = {
            'severe': {
                'Iron': '100-200mg daily',
                'Vitamin C': '500mg daily',
                'Vitamin B12': '1000mcg daily'
            },
            # ... similar structures for other severities
        }

    def get_recommendations(self, severity, is_vegetarian):
        diet_type = 'vegetarian' if is_vegetarian else 'non_vegetarian'
        return {
            'diet': self.diet_recommendations[severity][diet_type],
            'supplements': self.supplements[severity],
            'lifestyle_tips': self.get_lifestyle_tips(severity)
        }

    def get_lifestyle_tips(self, severity):
        # Add lifestyle recommendations based on severity
        pass