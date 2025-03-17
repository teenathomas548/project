from django.core.management.base import BaseCommand
from blood.models import Hospital, BloodRequest
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Add test blood request data'

    def handle(self, *args, **kwargs):
        # Get all hospitals
        hospitals = Hospital.objects.filter(is_active=True)
        
        if not hospitals:
            self.stdout.write(self.style.ERROR('No active hospitals found'))
            return

        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Generate data for each hospital
        for hospital in hospitals:
            # Generate 30 days of data
            for i in range(30):
                request_date = datetime.now().date() - timedelta(days=i)
                
                # Create 2-4 requests per day
                for _ in range(random.randint(2, 4)):
                    BloodRequest.objects.create(
                        hospital_name=hospital.hospital_name,
                        blood_group=random.choice(blood_groups),
                        quantity=random.randint(1, 5),
                        request_date=request_date,
                        requester_name=f"Dr. Test {random.randint(1, 10)}",
                        contact_number=f"+91{random.randint(7000000000, 9999999999)}",
                        status='Completed'
                    )

        self.stdout.write(self.style.SUCCESS('Successfully added test data'))