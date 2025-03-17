# blood/ml_model.py
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# bloodbank/blood/iron_predictor.py
class IronPredictor:
    @staticmethod
    def predict_iron_status(gender, hemoglobin, ferritin, transferrin_sat, stfr):
        # Define thresholds based on gender
        hb_threshold = 13.0 if gender == 'M' else 12.5
        
        # Check for iron deficiency
        if ferritin < 12 or (ferritin < 30 and transferrin_sat < 16):
            if hemoglobin < hb_threshold:
                return "Severe Iron Deficiency Anemia"
            return "Iron Deficiency"
        
        # Check for iron excess
        if ferritin > 200 or transferrin_sat > 45:
            return "Iron Excess"
            
        return "Normal Iron Status"

    @staticmethod
    def get_diet_plan(iron_status, gender):
        diet_plans = {
            "Severe Iron Deficiency Anemia": """
URGENT DIETARY RECOMMENDATIONS:
1. High-Iron Foods (Daily):
   - Lean red meat (3-4 times per week)
   - Organ meats (liver) twice weekly
   - Dark leafy greens (spinach, kale)
   - Fortified cereals
   
2. Iron Absorption Enhancers:
   - Vitamin C rich foods with every meal
   - Citrus fruits, berries, tomatoes
   - Avoid tea/coffee with meals
   
3. Supplements (Consult Doctor):
   - Iron supplements
   - Vitamin C supplements
   - Vitamin B12 and Folate
   
4. Meal Planning:
   - Space iron supplements from dairy products
   - Eat iron-rich foods on empty stomach
   - Include protein with every meal

MEDICAL ATTENTION REQUIRED
Schedule appointment with healthcare provider
""",
            "Iron Deficiency": """
DIETARY RECOMMENDATIONS:
1. Iron-Rich Foods:
   - Lean meats (beef, pork, lamb)
   - Fish and shellfish
   - Beans and lentils
   - Dark green vegetables
   
2. Optimization Tips:
   - Combine iron sources with vitamin C
   - Avoid calcium with iron-rich meals
   - Cook in cast iron cookware
   
3. Daily Essentials:
   - Fortified breakfast cereals
   - Nuts and seeds
   - Dried fruits (raisins, apricots)
   
4. Consider Supplements:
   - Consult doctor about iron supplements
   - Include vitamin C supplements
""",
            "Normal Iron Status": """
MAINTENANCE DIET:
1. Balanced Iron Intake:
   - Regular consumption of lean meats
   - Include plant-based iron sources
   - Eat variety of fruits and vegetables
   
2. Healthy Habits:
   - Maintain balanced diet
   - Regular exercise
   - Stay hydrated
""",
            "Iron Excess": """
IRON REDUCTION DIET:
1. Limit Iron-Rich Foods:
   - Reduce red meat intake
   - Avoid iron-fortified foods
   - Limit vitamin C with meals
   
2. Include These Foods:
   - Whole grains
   - Dairy products
   - Green tea between meals
   
3. Recommendations:
   - Avoid iron supplements
   - Regular blood tests
   - Consult healthcare provider
"""
        }
        
        base_plan = diet_plans.get(iron_status, "Consult healthcare provider")
        
        # Add gender-specific recommendations
        if gender == 'F':
            base_plan += """
            
Additional Recommendations for Women:
- Increase iron intake during menstruation
- Consider iron supplements during heavy periods
- Monitor iron levels regularly
"""
        
        return base_plan
