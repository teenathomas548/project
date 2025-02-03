from django import forms
from .models import Registration
from .models import Inventory
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from .models import Recipient, BloodType  # Adjust imports as per your models
from django.core.exceptions import ValidationError
from datetime import date
import re


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'password', 'phone_number', 'gender', 'blood_group', 'role']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'id': 'email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'password'})
    )

from .models import Campaign

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'start_date', 'end_date', 'location', 'description', 'is_active', 'is_deleted']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError("Campaign name cannot be empty.")
        
        if len(name) > 255:
            raise ValidationError("Campaign name must not exceed 255 characters.")
        
        # Check that the name contains only letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', name):
            raise ValidationError("Campaign name should only contain letters and spaces.")
        
        return name

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        
        if start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        
        return start_date

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        
        if end_date and start_date and end_date < start_date:
            raise ValidationError("End date must be after the start date.")
        
        return end_date

    def clean_location(self):
        location = self.cleaned_data.get('location')
        
        if not location:
            raise ValidationError("Location cannot be empty.")
        
        if len(location) > 255:
            raise ValidationError("Location must not exceed 255 characters.")
        
        return location

    def clean_description(self):
        description = self.cleaned_data.get('description')
        
        if not description:
            raise ValidationError("Description cannot be empty.")
        
        # Check that the description does not contain numbers
        if re.search(r'[0-9]', description):
            raise ValidationError("Description should not contain numbers.")
        
        return description

    def clean(self):
        cleaned_data = super().clean()
        is_active = cleaned_data.get('is_active')
        is_deleted = cleaned_data.get('is_deleted')

        if is_deleted and is_active:
            raise ValidationError("A deleted campaign cannot be marked as active.")
        
        return cleaned_data


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['blood_type', 'units_available', 'price', 'is_active']


from .models import BloodRequest

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['requester_name', 'blood_group', 'quantity', 'hospital_name', 'contact_number']
        widgets = {
            'blood_group': forms.Select(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')]),
        }



class RecipientEditForm(forms.ModelForm):
    class Meta:
        model = Registration  # Use the Registration model for recipient data
        fields = ['first_name', 'last_name', 'date_of_birth',  'phone_number', 'gender', 'blood_group']  

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=150)

from .models import DonorProfile  # Ensure you import the correct model

class DonorEditForm(forms.ModelForm):
    class Meta:
        model = DonorProfile  # Use the DonorProfile model for donor data
        fields = ['donor_name', 'email', 'date_of_birth', 'contact_number', 'blood_type']


class EditCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'start_date', 'end_date', 'description']  # Specify fields to edit
    
    # Optional: Customize widgets for better presentation
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2020, 2030)))
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2020, 2030)))
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        
        # Ensure start date is today or in the future
        if start_date < date.today():
            raise forms.ValidationError('Start date must be today or in the future.')

        return start_date

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        # Ensure end date is later than start date
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError('End date must be later than the start date.')

        return end_date



from .models import BloodType

class BloodInventorySearchForm(forms.Form):
    blood_type = forms.ModelChoiceField(queryset=BloodType.objects.all(), empty_label="Select Blood Group")



# forms.py


class HospitalRequestForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone_number', 'gender', 'blood_group']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        recipient = super().save(commit=False)
        # Set the role to 'recipient'
        recipient.role = 'recipient'
        if commit:
            recipient.save()
        return recipient

from django import forms
from .models import Hospital
import re

class HospitalRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        max_length=128,
        min_length=6,
        error_messages={
            'required': 'Please enter a password.',
            'min_length': 'Password should be at least 6 characters long.'
        }
    )

    class Meta:
        model = Hospital
        fields = ['hospital_name', 'phone_number', 'email', 'password', 'document']

    def clean_hospital_name(self):
        hospital_name = self.cleaned_data.get('hospital_name')
        if not re.match(r'^[A-Za-z\s]+$', hospital_name):
            raise forms.ValidationError("Hospital Name should contain only letters and spaces.")
        return hospital_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^[6-9]\d{9}$', phone_number):
            raise forms.ValidationError("Phone Number should start with 6, 7, 8, or 9 and be exactly 10 digits long.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            if not document.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF documents are allowed.")
            if document.size > 2 * 1024 * 1024:  # Optional: Limit file size to 2MB
                raise forms.ValidationError("File size should not exceed 2MB.")
        return document

class HospitalLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


# forms.py

from django import forms
from .models import Doctor

import re
from django import forms
from .models import Doctor
from django.contrib.auth.hashers import make_password

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['hospital_id', 'doctor_name', 'specialization', 'email', 'password']  # Added email and password fields
        widgets = {
            'hospital_id': forms.Select(),  # Dropdown for selecting a hospital
            'password': forms.PasswordInput(),  # Password input field
        }

    # Validation for doctor's name
    def clean_doctor_name(self):
        doctor_name = self.cleaned_data.get('doctor_name')
        if not re.match("^[a-zA-Z\s]+$", doctor_name):
            raise forms.ValidationError("Doctor's Name must contain only letters and spaces.")
        return doctor_name

    # Validation for specialization
    def clean_specialization(self):
        specialization = self.cleaned_data.get('specialization')
        if not re.match("^[a-zA-Z\s,]+$", specialization):
            raise forms.ValidationError("Specialization must contain only letters, commas, and spaces.")
        return specialization

    # Validation for email (EmailField automatically validates format)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Doctor.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    # Validation for password
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password  # Hashing the password before saving
    

class DoctorLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter your email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))



from .models import BloodApply

class BloodApplyForm(forms.ModelForm):
    class Meta:
        model = BloodApply
        fields = ['blood_type', 'quantity', 'hospital', 'urgency', 'patient_name', 'patient_age', 'reason']
        widgets = {
            'patient_age': forms.NumberInput(attrs={'min': 1}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'urgency': forms.Select(choices=[('normal', 'Normal'), ('emergency', 'Emergency')]),
            'reason': forms.Textarea(attrs={'placeholder': 'Please provide a reason for the blood application.', 'rows': 4}),
        }

from django import forms
from datetime import date  # Import date for comparison
from .models import Appointment  # Adjust this based on your actual model

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment  # Replace with your actual model
        fields = ['appointment_date', 'appointment_time']

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date <= date.today():
            raise forms.ValidationError("The appointment date must be in the future.")
        return appointment_date

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get('appointment_time')
        return appointment_time

from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import DonorProfile
import re

from django import forms
from .models import DonorProfile, BloodType

class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ['donor_name', 'date_of_birth', 'last_donation_date', 'contact_number', 'email', 'password', 'blood_type']
        widgets = {
            'password': forms.PasswordInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
        }
    # Validation for donor_name: Only letters and spaces allowed
    def clean_donor_name(self):
        donor_name = self.cleaned_data['donor_name']
        if not re.match(r"^[A-Za-z\s]+$", donor_name):  # Changed to raw string
            raise ValidationError("Name should contain only letters and spaces.")
        return donor_name

    # Validation for date_of_birth: Must be 18 years or older
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data['date_of_birth']
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

        if age < 18:
            raise ValidationError("You must be at least 18 years old to register.")
        return date_of_birth

    # Validation for contact_number: Must start with 6, 7, 8, or 9 and be exactly 10 digits
    def clean_contact_number(self):
        contact_number = self.cleaned_data['contact_number']
        if not re.match(r"^[6-9]\d{9}$", contact_number):  # Changed to raw string
            raise ValidationError("Contact number must start with 6, 7, 8, or 9 and contain exactly 10 digits.")
        return contact_number

    # Validation for email: Django automatically validates the email field, but you can extend it
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Changed to raw string
            raise ValidationError("Please enter a valid email address.")
        return email

    def clean_last_donation_date(self):
        last_donation_date = self.cleaned_data.get('last_donation_date')
        if last_donation_date:  # Check if last_donation_date is not None
            today = date.today()
            if last_donation_date > today:
                raise forms.ValidationError("Last donation date must be in the past.")
        return last_donation_date



class DonorLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))



from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class FirstTimeDonationForm(forms.Form):
    first_time_donor = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        widget=forms.RadioSelect,  # You can change this to a dropdown if you prefer
        label="Are you donating blood for the first time?"
    )


from .models import MedicalReport

class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['medical_report']  # Only allow the medical report to be uploaded
        widgets = {
            'medical_report': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




from django import forms
from .models import BloodApply, Doctor  # Assuming you have a Doctor model

class BloodApplyWithhospitalForm(forms.ModelForm):
    class Meta:
        model = BloodApply
        fields = ['blood_type', 'quantity', 'hospital', 'urgency', 'patient_name', 'patient_age', 'reason', 'doctor']
        widgets = {
            'patient_age': forms.NumberInput(attrs={'min': 1}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'urgency': forms.Select(choices=[('normal', 'Normal'), ('emergency', 'Emergency')]),
            'reason': forms.Textarea(attrs={'placeholder': 'Please provide a reason for the blood application.', 'rows': 4}),
        }

    # Add a doctor field with choices populated from the Doctor model
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(), 
        empty_label="Select a Doctor",
        widget=forms.Select(attrs={'class': 'form-control'})  # You can customize widget further if needed
    )
    
from django import forms
from .models import Admin

class AdminRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Admin
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

from django import forms
from .models import PlasmaRequest, Doctor  # Assuming you have a Doctor model


class PlasmaRequestForm(forms.ModelForm):
    class Meta:
        model = PlasmaRequest
        fields = ['blood_type', 'quantity', 'hospital', 'urgency', 'patient_name', 'patient_age', 'reason']
        widgets = {
            'patient_age': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Enter patient age'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Enter required quantity in units'}),
            'urgency': forms.Select(choices=[('normal', 'Normal'), ('emergency', 'Emergency')]),
            'reason': forms.Textarea(attrs={
                'placeholder': 'Please provide a reason for the blood application.',
                'rows': 4,
                'maxlength': 500,
            }),
        }
        error_messages = {
            'blood_type': {'required': 'Blood type is required.'},
            'quantity': {'required': 'Quantity is required.', 'min_value': 'Quantity must be at least 1.'},
            'hospital': {'required': 'Hospital name is required.'},
            'urgency': {'required': 'Please specify the urgency level.'},
            'patient_name': {'required': 'Patient name is required.'},
            'patient_age': {'required': 'Patient age is required.', 'invalid': 'Enter a valid age.'},
            'reason': {'required': 'Reason for the plasma request is required.'},
        }

    def clean_patient_name(self):
        patient_name = self.cleaned_data.get('patient_name')
        if not patient_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Patient name must contain only alphabetic characters.")
        return patient_name

    def clean_patient_age(self):
        patient_age = self.cleaned_data.get('patient_age')
        if patient_age < 1 or patient_age > 120:
            raise forms.ValidationError("Patient age must be between 1 and 120.")
        return patient_age

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1 unit.")
        return quantity

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if len(reason) < 10:
            raise forms.ValidationError("Reason must be at least 10 characters long.")
        return reason
    
    def clean_hospital(self):
        hospital = self.cleaned_data.get('hospital')
        if not hospital.replace(' ', '').isalpha():
            raise forms.ValidationError("Hospital name must contain only alphabetic characters.")
        return hospital

# forms.py
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={'placeholder': 'Your feedback here...', 'rows': 5}),
        }
