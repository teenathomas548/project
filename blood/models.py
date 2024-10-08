from django.db import models
from datetime import date


from django.db import models

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
    is_active = models.BooleanField(default=True)  # New field for enabling/disabling


    def __str__(self):
        return self.name 
    is_deleted = models.BooleanField(default=False)  # Field to mark campaigns as "deleted"

    # Method to check expiration and flag campaigns as deleted
    def check_and_flag_expired(self):
        if self.end_date < date.today():
            self.is_deleted = True
            self.save()

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
    blood_type = models.ForeignKey(BloodType, on_delete=models.CASCADE, db_column='blood_type_id')  # Referencing 'blood_type_id'
    user = models.ForeignKey('Registration', on_delete=models.CASCADE,db_column='user_id')  # Adjust the field name as per your project

    def __str__(self):
        return f"Recipient: {self.user.first_name} {self.user.last_name}, Blood Type: {self.blood_type.blood_group}"


class BloodRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Fulfilled', 'Fulfilled'),
        ('Cancelled', 'Cancelled'),
    ]
    
    request_id = models.AutoField(primary_key=True)
    recipient_id = models.ForeignKey('Recipient', on_delete=models.CASCADE)
    blood_type_id = models.ForeignKey('BloodType', on_delete=models.CASCADE)
    units_requested = models.IntegerField(null=True, blank=True)
    request_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=REQUEST_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'Request {self.request_id} - {self.status}'