from datetime import datetime, timedelta
from django.utils import timezone

class HealthRiskAnalyzer:
    def assess_risk(self, donor):
        risk_factors = []
        recommendations = []
        overall_risk = 'low'

        # Age check based on date_of_birth
        today = timezone.now().date()
        age = today.year - donor.date_of_birth.year - (
            (today.month, today.day) < (donor.date_of_birth.month, donor.date_of_birth.day)
        )

        if age < 18:
            risk_factors.append({
                'severity': 'high',
                'description': 'Donor is under 18 years old'
            })
            recommendations.append('Must be at least 18 years old to donate blood')
            overall_risk = 'high'
        elif age > 65:
            risk_factors.append({
                'severity': 'medium',
                'description': 'Donor is over 65 years old'
            })
            recommendations.append('Additional medical screening may be required')
            overall_risk = max(overall_risk, 'medium')

        # Last donation date check
        if donor.last_donation_date:
            days_since_donation = (today - donor.last_donation_date).days
            if days_since_donation < 90:
                risk_factors.append({
                    'severity': 'high',
                    'description': f'Only {days_since_donation} days since last donation'
                })
                next_eligible_date = donor.last_donation_date + timedelta(days=90)
                recommendations.append(f'Wait until {next_eligible_date.strftime("%Y-%m-%d")} to donate again')
                overall_risk = 'high'
            elif days_since_donation < 120:
                risk_factors.append({
                    'severity': 'low',
                    'description': 'Recent donation within 4 months'
                })
                recommendations.append('Monitor iron levels before next donation')

        # Blood type check
        if not donor.blood_type:
            risk_factors.append({
                'severity': 'medium',
                'description': 'Blood type not recorded'
            })
            recommendations.append('Complete blood type testing before donation')
            overall_risk = max(overall_risk, 'medium')

        # Activity status check
        if not donor.is_active:
            risk_factors.append({
                'severity': 'high',
                'description': 'Donor account is currently inactive'
            })
            recommendations.append('Contact blood bank administration to reactivate account')
            overall_risk = 'high'

        # Points-based assessment
        if donor.points < 10:
            recommendations.append('Complete donor profile and participate in blood drives to earn more points')
        elif donor.points >= 50:
            recommendations.append('Eligible for premium donor benefits')

        # Add general recommendations if no high risks found
        if overall_risk == 'low':
            recommendations.extend([
                'Maintain healthy lifestyle',
                'Stay hydrated before donation',
                'Get adequate rest before donation',
                'Eat iron-rich foods regularly'
            ])

        return {
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'overall_risk': overall_risk,
            'donor_points': donor.points,
            'age': age,
            'next_eligible_date': (donor.last_donation_date + timedelta(days=90)) if donor.last_donation_date else None
        }