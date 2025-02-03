
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
