
from django.db import models
from datetime import date


class Admin(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blood_admin'

    def __str__(self):
        return self.email


class Campaign(models.Model):
    campaign_id = models.AutoField(primary_key=True)  # Unique identifier for each campaign
    name = models.CharField(max_length=255)           # Name of the campaign
    start_date = models.DateField()                   # Start date of the campaign
    end_date = models.DateField()                     # End date of the campaign
    location = models.CharField(max_length=255)       # Location of the campaign
    description = models.TextField()                  # Description of the campaign
    is_active = models.BooleanField(default=True)     # Field for enabling/disabling campaign
    is_deleted = models.BooleanField(default=False)   # Field to mark campaigns as "deleted"

    # Method to check expiration and flag campaigns as deleted
    def check_and_flag_expired(self):
        if self.end_date < date.today():
            self.is_deleted = True
            self.save()

    def __str__(self):
        return self.name


class BloodType(models.Model):
    blood_type_id = models.AutoField(primary_key=True)
    blood_group = models.CharField(max_length=3)

    def __str__(self):
        return self.blood_group


class Registration(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    blood_group = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)  # Default: user is active
    reset_token = models.CharField(max_length=255, null=True, blank=True)  # Token for password reset

    class Meta:
        db_table = 'registrations'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    blood_type = models.ForeignKey('BloodType', on_delete=models.CASCADE)
    units_available = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)  # New field to enable/disable the record

    def __str__(self):
        return f"Inventory {self.inventory_id} - {self.blood_type.blood_group}"


class BloodDonor(models.Model):
    donor_id = models.AutoField(primary_key=True)  # Primary key for the BloodDonor model
    last_donation_date = models.DateField(null=True, blank=True)  # Date of last donation, optional
    eligibility_status = models.CharField(max_length=50, default='Eligible')  # Default eligibility status
    user = models.ForeignKey(Registration, on_delete=models.CASCADE)  # Foreign key to Registration
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)  # Foreign key to BloodType

    class Meta:
        db_table = 'blood_donors'  # Table name in the database

    def __str__(self):
        return f"Donor ID: {self.donor_id} - User: {self.user.first_name} {self.user.last_name}"


class Recipient(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)  # Referencing 'blood_type_id'
    user = models.ForeignKey('Registration', on_delete=models.CASCADE)  # Adjust the field name as per your project

    def __str__(self):
        return f"Recipient: {self.user.first_name} {self.user.last_name}, Blood Type: {self.blood_type.blood_group}"


class BloodRequest(models.Model):
    REQUEST_STATUSES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    requester_name = models.CharField(max_length=100)
    blood_group = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # in units (ml or pints)
    hospital_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15)
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=REQUEST_STATUSES)

    def __str__(self):
        return f"{self.requester_name} - {self.blood_group}"
    
    
class Donation(models.Model):
    donor = models.ForeignKey(Registration, on_delete=models.CASCADE)  # Link to Registration model
    blood_group = models.ForeignKey(BloodType, on_delete=models.CASCADE)  # Link to BloodType model
    donation_date = models.DateField(default=date.today)  # Defaults to current date
    location = models.CharField(max_length=255)  # Location of the donation
    notes = models.TextField(null=True, blank=True)  # Optional notes for the donation (e.g., health concerns, special requests)

    class Meta:
        db_table = 'donations'  # Custom table name

    def __str__(self):
        # Display donor's full name and blood group
        return f"{self.donor.first_name} {self.donor.last_name} - {self.blood_group.name} on {self.donation_date}"



class Hospital(models.Model):
    hospital_id = models.AutoField(primary_key=True)
    hospital_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=128)  # Add this field for password storage

    def __str__(self):
        return self.hospital_name


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)  # Unique identifier for each doctor
    hospital_id = models.ForeignKey('Hospital', on_delete=models.CASCADE)  # Foreign key linked to hospital_id in Hospital model
    doctor_name = models.CharField(max_length=255)  # Name of the doctor
    specialization = models.CharField(max_length=255)  # Specialization of the doctor
    email = models.EmailField(unique=True)  # Email field for the doctor
    password = models.CharField(max_length=255)  # Password field for the doctor

    def __str__(self):
        return self.doctor_name
    


class BloodApply(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),   
        ('fulfilled', 'Fulfilled'),
        ('rejected', 'Rejected'),
    ]

    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    quantity = models.IntegerField(help_text="Quantity in units (e.g., 1 unit = 500ml)")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='blood_applications')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='blood_requests')  # New doctor field
    request_date = models.DateTimeField(auto_now_add=True)
    urgency = models.CharField(max_length=50, null=True, blank=True, choices=[('normal', 'Normal'), ('emergency', 'Emergency')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    patient_name = models.CharField(max_length=255, null=True, blank=True)  # Optional, can be left blank for general requests
    patient_age = models.IntegerField(null=True, blank=True)  # Optional, age of the patient (if applicable)
    reason = models.TextField(blank=True, null=True)  # New reason field

    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.blood_type.blood_group} - {self.status}"

    def fulfill_request(self):
        """Fulfill the blood application by updating inventory and changing the status."""
        try:
            # Check if the requested blood type is available in the inventory
            inventory = Inventory.objects.get(blood_type=self.blood_type, is_active=True)
            if inventory.update_inventory(self.quantity):
                self.status = 'fulfilled'
                self.save()
                return True
            else:
                self.status = 'rejected'
                self.save()
                return False
        except Inventory.DoesNotExist:
            self.status = 'rejected'
            self.save()
            return False
        

class DonorProfile(models.Model):
    donor_id = models.AutoField(primary_key=True)
    donor_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    last_donation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    blood_type = models.ForeignKey(BloodType, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'donor_profiles'

    def __str__(self):
        return self.donor_name



from django.db import models
from django.utils import timezone
from .models import DonorProfile

class Appointment(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, default='Scheduled')  # Example: 'Scheduled', 'Completed', 'Cancelled'

    class Meta:
        db_table = 'appointments'



class MedicalReport(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    medical_report = models.FileField(upload_to='medical_reports/')
    submission_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'medical_reports'