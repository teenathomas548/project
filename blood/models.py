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
    plasma_available = models.IntegerField(default=0)  # New field to track plasma units
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
    is_active = models.BooleanField(default=True)
    document = models.FileField(upload_to='document/', blank=True, null=True)  # Field for uploading hospital documents
    is_approved = models.BooleanField(default=False)  # Track approval status


    def __str__(self):
        return self.hospital_name


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)  # Unique identifier for each doctor
    hospital_id = models.ForeignKey('Hospital', on_delete=models.CASCADE)  # Foreign key linked to hospital_id in Hospital model
    doctor_name = models.CharField(max_length=255)  # Name of the doctor
    specialization = models.CharField(max_length=255)  # Specialization of the doctor
    email = models.EmailField(unique=True)  # Email field for the doctor
    password = models.CharField(max_length=255)  # Password field for the doctor
    is_active = models.BooleanField(default=True)

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
        
from datetime import timedelta


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
    reset_token = models.CharField(max_length=32, blank=True, null=True)  # Add this field for storing reset token
    points = models.IntegerField(default=0)  # New field for gamification


    class Meta:
        db_table = 'donor_profiles'

    def __str__(self):
        return self.donor_name
    def can_schedule_appointment(self):
        # Check if the last donation date is available
        if self.last_donation_date:
            # Calculate the next eligible appointment date
            next_appointment_date = self.last_donation_date + timedelta(days=90)  # 3 months = 90 days
            return timezone.now().date() >= next_appointment_date
        return True  



from django.db import models
from django.utils import timezone
from .models import DonorProfile

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
        ('Cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        db_table = 'appointments'


from django.utils import timezone

class MedicalReport(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    medical_report = models.FileField(upload_to='medical_reports/')
    submission_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'medical_reports'




from django.db import models

class PlateletsDonation(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A Positive (A+)'),
        ('A-', 'A Negative (A-)'),
        ('B+', 'B Positive (B+)'),
        ('B-', 'B Negative (B-)'),
        ('O+', 'O Positive (O+)'),
        ('O-', 'O Negative (O-)'),
        ('AB+', 'AB Positive (AB+)'),
        ('AB-', 'AB Negative (AB-)'),
    ]

    name = models.CharField(max_length=100, verbose_name="Full Name")
    email = models.EmailField(max_length=100, unique=True, verbose_name="Email Address")
    phone = models.CharField(max_length=15, verbose_name="Contact Number")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, verbose_name="Blood Type")
    donation_date = models.DateField(verbose_name="Available Date", null=True, blank=True)
    donation_time = models.TimeField(verbose_name="Available Time", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Submission Time")

    def __str__(self):
        return f"{self.name} ({self.blood_type})"

from django.db import models

class PlasmaDonation(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A Positive (A+)'),
        ('A-', 'A Negative (A-)'),
        ('B+', 'B Positive (B+)'),
        ('B-', 'B Negative (B-)'),
        ('O+', 'O Positive (O+)'),
        ('O-', 'O Negative (O-)'),
        ('AB+', 'AB Positive (AB+)'),
        ('AB-', 'AB Negative (AB-)'),
    ]

    name = models.CharField(max_length=100, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=15, verbose_name="Contact Number")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, verbose_name="Blood Type")
    donation_date = models.DateField(verbose_name="Donation Date")
    donation_time = models.TimeField(verbose_name="Donation Time")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.name} - {self.blood_type}"


class PlasmaRequest(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    URGENCY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    REQUEST_STATUSES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    patient_name = models.CharField(max_length=255)
    patient_age = models.PositiveIntegerField()
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Enter quantity in units")
    hospital = models.CharField(max_length=255)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    reason = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=REQUEST_STATUSES, default='pending')  # Added status field

    def __str__(self):
        return f"{self.patient_name} - {self.blood_type} - {self.hospital}"


# models.py
from django.db import models
from .models import DonorProfile  # Import DonorProfile model

class Feedback(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.donor.donor_name} on {self.created_at}"



from django.shortcuts import render, redirect
from .models import Appointment

def manage_appointments(request):
    appointments = Appointment.objects.all()  # Fetch all appointments

    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        # Update the status
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = new_status
        appointment.save()

        return redirect("manage_appointments")  # Reload the page after updating

    return render(request, "manage_appointments.html", {"appointments": appointments})


from django.db import models
from django.contrib.auth.models import User

class BloodDonationRequest(models.Model):
    TIME_CHOICES = [
        ('morning', 'Morning (9 AM - 12 PM)'),
        ('afternoon', 'Afternoon (2 PM - 5 PM)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey('DonorProfile', on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=20, choices=TIME_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Donation Request - {self.donor.full_name} ({self.preferred_date})"

class BasicScreening(models.Model):
    donation_request = models.OneToOneField(BloodDonationRequest, on_delete=models.CASCADE)
    blood_pressure = models.CharField(max_length=20)  # e.g., "120/80"
    temperature = models.DecimalField(max_digits=4, decimal_places=1)  # e.g., 98.6
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # in kg
    pulse_rate = models.IntegerField()  # beats per minute
    hemoglobin = models.DecimalField(max_digits=4, decimal_places=1)  # g/dL
    is_eligible = models.BooleanField(default=False)
    screening_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Screening for {self.donation_request.donor.donor_name}"
    

class BloodTest(models.Model):
    donation = models.OneToOneField('BloodDonationRequest', on_delete=models.CASCADE)
    hiv = models.BooleanField(default=False)
    hepatitis_b = models.BooleanField(default=False)
    hepatitis_c = models.BooleanField(default=False)
    syphilis = models.BooleanField(default=False)
    malaria = models.BooleanField(default=False)
    hemoglobin = models.DecimalField(max_digits=4, decimal_places=1)
    test_date = models.DateTimeField(auto_now_add=True)
    tested_by = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    is_safe = models.BooleanField(default=False)

    def __str__(self):
        return f"Test for {self.donation.donor.donor_name} on {self.test_date}"

    def check_safety(self):
        self.is_safe = not (self.hiv or self.hepatitis_b or 
                           self.hepatitis_c or self.syphilis or 
                           self.malaria)
        self.save()
        
        # Update donation status based on test results
        if self.is_safe:
            self.donation.status = 'completed'
        else:
            self.donation.status = 'rejected'
        self.donation.save()

    class Meta:
        ordering = ['-test_date']


from django.db import models
from datetime import datetime

class DonorRecipientMatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]

    blood_request = models.ForeignKey(BloodApply, on_delete=models.CASCADE)
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    match_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ml_confidence = models.FloatField()
    donor_response = models.BooleanField(null=True)
    
    class Meta:
        ordering = ['-match_score']

    def __str__(self):
        return f"{self.donor.donor_name} - {self.blood_request.blood_type}"
    

class BloodDemandPrediction(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    predicted_demand = models.IntegerField()
    prediction_date = models.DateField()
    confidence_score = models.FloatField()
    actual_demand = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']

    def __str__(self):
        return f"{self.hospital} - {self.blood_type} - {self.prediction_date}"

class DemandHistory(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    demand_date = models.DateField()
    quantity = models.IntegerField()
    is_holiday = models.BooleanField(default=False)
    season = models.CharField(max_length=20)  # summer, winter, monsoon, etc.
    day_of_week = models.IntegerField()  # 0-6 for Monday-Sunday
    is_emergency = models.BooleanField(default=False)

    class Meta:
        ordering = ['-demand_date']


from django.db import models
from django.utils import timezone

class BloodTransfer(models.Model):
    TRANSFER_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    PRIORITY_LEVELS = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ]

    transfer_id = models.AutoField(primary_key=True)
    from_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='transfers_sent')
    to_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='transfers_received')
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE)
    units = models.IntegerField()
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='normal')
    notes = models.TextField(blank=True)
    # Removed the created_by field since Registration model doesn't exist

    def __str__(self):
        return f"Transfer {self.transfer_id}: {self.from_hospital} to {self.to_hospital}"

    class Meta:
        ordering = ['-request_date']
        

class DonorIronStatus(models.Model):
    donor = models.OneToOneField(DonorProfile, on_delete=models.CASCADE)
    serum_ferritin = models.FloatField(help_text="Iron storage levels (ng/ml)")
    total_iron_binding_capacity = models.FloatField(help_text="TIBC (µg/dL)")
    transferrin_saturation_index = models.FloatField(help_text="TSI (%)")
    hemoglobin_level = models.FloatField(help_text="Hemoglobin (g/dL)")
    donation_count_last_year = models.IntegerField()
    iron_deficiency_status = models.CharField(max_length=50, blank=True)
    diet_plan = models.TextField(blank=True)

    def classify_deficiency(self):
        """Classify donor's iron deficiency status and assign a diet plan"""
        if self.serum_ferritin < 12:
            if self.transferrin_saturation_index < 16:
                self.iron_deficiency_status = "Iron Deficiency Anemia"
                self.diet_plan = "High-iron meats (liver, beef), dark leafy greens, vitamin C (oranges), legumes."
            else:
                self.iron_deficiency_status = "Iron Deficient"
                self.diet_plan = "Iron-rich grains, lentils, nuts, fortified cereals, fish, and citrus fruits."
        else:
            self.iron_deficiency_status = "Normal"
            self.diet_plan = "Balanced diet with moderate iron intake."

    def save(self, *args, **kwargs):
        self.classify_deficiency()
        super(DonorIronStatus, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.donor.donor_name} - {self.iron_deficiency_status}"


from django.db import models
from django.utils import timezone

class BloodRecipient(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    recipient_name = models.CharField(max_length=100)
    blood_type = models.ForeignKey(BloodType, on_delete=models.SET_NULL, null=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    medical_history = models.TextField()
    password = models.CharField(max_length=100)
    registration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.recipient_name} ({self.blood_type})"


from django.db import models

class IronPrediction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=10)
    hemoglobin = models.FloatField()
    mch = models.FloatField()
    mchc = models.FloatField()
    mcv = models.FloatField()
    severity = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Prediction for {self.gender} on {self.date.strftime('%Y-%m-%d')}"