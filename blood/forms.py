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

class LoginForm(forms.Form):
    email = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


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

class DonorEditForm(forms.ModelForm):
    class Meta:
        model = Registration  # Use the Registration model for recipient data
        fields = ['first_name', 'last_name', 'date_of_birth',  'phone_number', 'gender','email']



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
