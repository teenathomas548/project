from pyexpat.errors import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from .forms import RegistrationForm
from django.views.generic import UpdateView
from .models import Registration
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Campaign
from .forms import CampaignForm
from django.utils import timezone
from .models import Inventory,BloodType
from django.core.exceptions import ValidationError
from .models import Recipient
from django.db.models import Count, Sum  # Import Sum here
from datetime import date
from .forms import BloodRequestForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Registration
from .models import Admin  # Assuming you have a BloodAdmin model
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from .forms import EditCampaignForm
from.models import BloodDonor

# About page view
def about(request):
    return render(request, 'about.html')



def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('date_of_birth')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        blood_group_value = request.POST.get('blood_group')  # The string like 'B+'
        role = request.POST.get('role')

        # Check if email already exists in the Registration table
        if Registration.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please use a different email.')
            return redirect('register')

        # Fetch the correct BloodType instance using the 'blood_group' field
        try:
            blood_group = BloodType.objects.get(blood_group=blood_group_value)
        except BloodType.DoesNotExist:
            messages.error(request, 'Invalid blood group selected.')
            return redirect('register')

        # Create a Registration object and save it
        registration = Registration.objects.create(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            email=email,
            password=password,
            phone_number=phone_number,
            gender=gender,
            blood_group=blood_group,  # Assign the BloodType instance correctly
            role=role
        )

        # Store additional data based on the role
        if role == 'recipient':
            Recipient.objects.create(user=registration, blood_type=blood_group)
        elif role == 'donate':
            BloodDonor.objects.create(user=registration, blood_type=blood_group)

        return redirect('login')
    else:
        return render(request, 'register.html')


    

def userhome(request):
    """
    Render the user home page.
    """
    return render(request, 'userhome.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DonorProfile, Doctor, Hospital, Admin
from .forms import LoginForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DonorProfile, Doctor, Hospital, Admin  # Ensure these models are imported
from .forms import LoginForm  # Assuming you have a LoginForm defined

def custom_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check for Donor
            donor = DonorProfile.objects.filter(email=email).first()
            if donor:
                if donor.is_active:  # Ensure donor is active
                    if password == donor.password:  # Direct password comparison
                        request.session['donor_id'] = donor.donor_id
                        return redirect('donor_dashboard')
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
                    return render(request, 'login.html', {'form': form})

            # Check for Doctor
            doctor = Doctor.objects.filter(email=email).first()
            if doctor:
                if doctor.is_active:  # Ensure doctor is active
                    if password == doctor.password:  # Direct password comparison
                        request.session['doctor_id'] = doctor.doctor_id
                        return redirect('doctor_dashboard')
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
                    return render(request, 'login.html', {'form': form})

            # Check for Hospital
            hospital = Hospital.objects.filter(email=email).first()
            if hospital:
                if hospital.is_approved:
                    if password == hospital.password:  # Direct password comparison
                        request.session['hospital_id'] = hospital.hospital_id
                        return redirect('hospital_dashboard')
                    else:
                        messages.error(request, 'Invalid password.')
                        return render(request, 'login.html', {'form': form})
                else:
                    messages.error(request, "Your account is awaiting admin approval.")
                    return render(request, 'login.html', {'form': form})

            # Check for Admin
            admin_user = Admin.objects.filter(email=email).first()
            if admin_user:
                if admin_user.is_active:  # Ensure admin is active
                    if password == admin_user.password:  # Direct password comparison
                        request.session['admin_id'] = admin_user.id
                        return redirect('blood_admin')
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
                    return render(request, 'login.html', {'form': form})

            # If no valid user is found
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()  # Create an empty form for GET requests

    return render(request, 'login.html', {'form': form})

# Render the login template
def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Fetch the admin user using Django ORM
            try:
                admin_user = Admin.objects.get(email=email)

                # Check if the provided password matches the stored password
                if admin_user.password == password:  # Consider using hashed passwords for security
                    # Set user in session
                    request.session['email'] = admin_user.email
                    return redirect('blood_admin')  # Redirect to a page after successful login
                else:
                    messages.error(request, 'Invalid username or password')

            except Admin.DoesNotExist:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
def home(request):
    # Fetch only active campaigns
    active_campaigns = Campaign.objects.filter(is_active=True)
    context = {
        'campaigns': active_campaigns,
    }
    return render(request, 'home.html', context)


def userrhome(request):
    return render(request, 'userrhome.html')

from django.shortcuts import render
from django.db.models import Sum
from .models import Registration, Inventory, BloodRequest

from django.shortcuts import render
from django.db.models import Sum
from .models import Registration, Inventory, BloodRequest

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Registration, Inventory, BloodApply
from django.contrib import messages

def blood_admin(request):
    # Total donors count
    total_donors = DonorProfile.objects.count()  # Get total count of all donors

    # Total available blood units
    blood_units = Inventory.objects.aggregate(total_units=Sum('units_available'))['total_units'] or 0

    # Pending requests count
    pending_requests = BloodApply.objects.filter(status='pending').count()
    
    # Urgent requests count
    urgent_requests = BloodApply.objects.filter(status='urgent').count()

    # Completed requests count
    completed_requests = BloodApply.objects.filter(status='approved').count()

    # Fetch recent activities dynamically, prioritizing pending requests
    recent_activities = [
        {
            "date": request.request_date,
            "doctor": request.doctor.doctor_name,
            "patient": request.patient_name,
            "hospital": request.hospital.hospital_name,
            "blood_group": request.blood_type.blood_group,
            "status": request.status,
            "id": request.id
        }
        for request in BloodApply.objects.order_by('-request_date').filter(status='pending')[:5]  # Limit to 5 recent pending requests
    ] + [
        {
            "date": request.request_date,
            "doctor": request.doctor.doctor_name,
            "patient": request.patient_name,
            "hospital": request.hospital.hospital_name,
            "blood_group": request.blood_type.blood_group,
            "status": request.status,
            "id": request.id
        }
        for request in BloodApply.objects.order_by('-request_date').exclude(status='pending')[:5]  # Get the next 5 most recent non-pending requests
    ][:5]  # Ensure total activities do not exceed 5

    context = {
        "total_donors": total_donors,
        "blood_units": blood_units,
        "pending_requests": pending_requests,
        "urgent_requests": urgent_requests,
        "completed_requests": completed_requests,
        "recent_activities": recent_activities,
    }

    return render(request, 'blood_admin.html', context)

def approve_request(request, request_id):
    blood_request = get_object_or_404(BloodApply, id=request_id)
    
    # Update the request status to approved
    blood_request.status = 'approved'
    blood_request.save()

    # Decrease the available blood units based on the correct field name
    inventory_entry = get_object_or_404(Inventory, blood_type=blood_request.blood_type)  # Use blood_type instead of blood_group
    if inventory_entry.units_available > 0:
        inventory_entry.units_available -= 1  # Decrease the blood unit count
        inventory_entry.save()
        messages.success(request, 'The request has been successfully approved, and blood availability has been updated.')
    else:
        messages.warning(request, 'Blood unit not available. Request cannot be approved.')

    return redirect('blood_admin')


def all_pending_requests(request):
    # Fetch all pending requests
    pending_requests = BloodApply.objects.filter(status='pending').order_by('-request_date')

    context = {
        "pending_requests": pending_requests,
    }

    return render(request, 'all_pending_requests.html', context)  # Template for displaying all pending requests


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Registration  # Make sure to import your Registration model

def disable_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    user.is_active = False
    user.save()

    # Send email notification to the user
    send_mail(
        'Account Disabled',
        f'Dear {user.first_name},\n\nYour account has been temporarily suspended due to a violation of our terms of service. Please review the terms and contact support for more information.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    messages.success(request, f'{user.first_name} {user.last_name} has been disabled and notified via email.')
    return redirect('manage_users')

def enable_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'{user.first_name} {user.last_name} has been enabled.')
    return redirect('manage_users')


def show_donors(request):
    donors = Registration.objects.filter(role='donor')  # Fetch only donors
    return render(request, 'donors.html', {'donors': donors})

def show_recipients(request):
    recipients = Registration.objects.filter(role='recipient')  # Fetch only recipients
    return render(request, 'recipients.html', {'recipients': recipients})

def manage_users(request):
    users = Registration.objects.all()  # Get all users
    return render(request, 'manage_users.html', {'users': users})



from django.shortcuts import render, get_object_or_404
from .models import DonorProfile, Appointment
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def donor_dashboard(request):
    if 'donor_id' not in request.session:
        return render(request, 'error.html', {'message': 'Donor not logged in.'})

    donor = get_object_or_404(DonorProfile, donor_id=request.session['donor_id'])
    
    logger.debug(f"Donor ID: {donor.donor_id}")

    upcoming_appointments = Appointment.objects.filter(
        donor=donor,
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date')

    upcoming_count = upcoming_appointments.count()
    logger.debug(f"Upcoming Appointments Count: {upcoming_count}")

    past_appointments = Appointment.objects.filter(
        donor=donor,
        appointment_date__lt=timezone.now().date()
    ).order_by('-appointment_date')

    if donor.last_donation_date:
        days_since_last_donation = (timezone.now().date() - donor.last_donation_date).days
        if days_since_last_donation >= 56:
            eligibility_status = "Eligible for donation"
        else:
            eligibility_status = f"Not eligible for donation until {donor.last_donation_date + timedelta(days=56)}"
    else:
        eligibility_status = "Eligible for first-time donation"
    
    first_time_donor = not donor.last_donation_date

    context = {
        'donor': donor,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'eligibility_status': eligibility_status,
        'first_time_donor': first_time_donor,
        'blood_type': donor.blood_type.blood_group if donor.blood_type else "Not specified",
        'upcoming_count': upcoming_count,
        'past_count': past_appointments.count(),
    }

    return render(request, 'donor_dashboard.html', context)


def campaign_list(request):
    campaigns = Campaign.objects.all()  # Fetch all campaigns from the database
    return render(request, 'campaign_list.html', {'campaigns': campaigns})

def add_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            # Validation: Start date cannot be in the past
            if start_date < date.today():
                form.add_error('start_date', "Start date cannot be in the past.")

            # Validation: End date cannot be before the start date
            if end_date < start_date:
                form.add_error('end_date', "End date cannot be earlier than the start date.")

            # If no errors are added, save the form
            if not form.errors:
                form.save()
                return redirect('manage_campaigns')
    else:
        form = CampaignForm()

    return render(request, 'add_campaign.html', {'form': form})

def disable_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    campaign.is_active = False  # Set is_active to False
    campaign.save()
    messages.success(request, f'Campaign "{campaign.name}" has been disabled.')
    return redirect('manage_campaigns')  # Redirect back to the campaign management page

def enable_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    campaign.is_active = True  # Set is_active to True
    campaign.save()
    messages.success(request, f'Campaign "{campaign.name}" has been enabled.')
    return redirect('manage_campaigns') 

# View to edit a campaign
def campaign_edit(request, campaign_id):
    campaign = get_object_or_404(Campaign, campaign_id=campaign_id)  
    if request.method == 'POST':
        form = EditCampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect('manage_campaigns')
    else:
        form = EditCampaignForm(instance=campaign)
    return render(request, 'campaign_edit.html', {'form': form, 'action': 'Edit'})

# View to delete a campaign

def manage_campaigns(request):
    if request.method == 'POST':
        # Handle form submission to add a new campaign
        name = request.POST['name']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        location = request.POST['location']
        description = request.POST['description']

        # Create a new campaign instance and save it
        Campaign.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            location=location,
            description=description
        )
        return redirect('manage_campaigns')

    # Retrieve existing campaigns to display
    campaigns = Campaign.objects.all()
    return render(request, 'manage_campaigns.html', {'campaigns': campaigns})

def recipient_dashboard(request):
    recipients = Registration.objects.filter(role='recipient')
    return render(request, 'recipient_dashboard.html', {'recipients': recipients})

def logout_view(request):
    if request.session:
        request.session.flush()  # Clears all session data
    return redirect('login') 

def latest_campaigns(request):
    now = timezone.now().date()
    
    # Disable expired campaigns
    expired_campaigns = Campaign.objects.filter(end_date__lt=now, is_active=True)
    expired_campaigns.update(is_active=False)

    # Fetch only active campaigns
    campaigns = Campaign.objects.filter(is_active=True)

    return render(request, 'latest_campaigns.html', {'campaigns': campaigns})

def logout_view(request):
    try:
        # Remove session data or cookies related to authentication
        del request.session['user_id']  # Example for session-based logout
    except KeyError:
        pass  # Session was already cleared or doesn't exist
    
    # Optionally, you can clear the entire session
    request.session.flush()

    # Redirect to a specific page after logging out
    return redirect('login')

def recipient_home(request):
    # Assuming the recipient is the currently logged-in user
    recipient = request.user
    
    # Filter blood requests by the recipient's name or another appropriate field
    blood_requests_count = BloodRequest.objects.filter(id=recipient.id ).count()
    print(blood_requests_count)
    
    # Pass the count to the template
    context = {
        'recipient': recipient,
        'blood_requests_count': blood_requests_count,
    }
    return render(request, 'recipient_home.html', context)


def inventory_list(request):
    inventory = Inventory.objects.all()  # Fetch all inventory records
    return render(request, 'inventory_list.html', {'inventory': inventory})

# View to enable a disabled inventory record
def enable_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.is_active = True
    inventory.save()
    return redirect('inventory_list')

# View to disable an active inventory record
def disable_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.is_active = False
    inventory.save()
    return redirect('inventory_list')


def add_inventory(request):
    if request.method == 'POST':
        blood_type_id = request.POST.get('blood_type_id')
        units_available = request.POST.get('units_available')
        price = request.POST.get('price')

        # Create a new inventory record
        inventory = Inventory.objects.create(
            blood_type_id=blood_type_id,
            units_available=units_available,
            price=price,
            is_active=True  # Set default active status
        )

        return redirect('inventory_list')  # Redirect to the inventory list page

    # If GET request, render the form
    blood_types = BloodType.objects.all()  # Fetch all blood types for the dropdown
    return render(request, 'add_inventory.html', {'blood_types': blood_types})




def edit_inventory(request, inventory_id):
    # Fetch the inventory item to edit
    inventory = get_object_or_404(Inventory, inventory_id=inventory_id)
    blood_types = BloodType.objects.all()  # Fetch all blood types for the dropdown

    if request.method == 'POST':
        # Get data from the form
        blood_type_id = request.POST.get('blood_type_id')
        units_available = request.POST.get('units_available')
        price = request.POST.get('price')

        # Update inventory object with new data
        inventory.blood_type_id = blood_type_id
        inventory.units_available = units_available
        inventory.price = price

        try:
            inventory.full_clean()  # Validate data
            inventory.save()  # Save changes to the database
            return redirect('inventory_list')  # Redirect to inventory list after successful update
        except ValidationError as e:
            # If validation fails, render the template again with error messages
            context = {
                'inventory': inventory,
                'blood_types': blood_types,
                'errors': e.messages,
            }
            return render(request, 'edit_inventory.html', context)

    # Render the template with the inventory item and blood types
    context = {
        'inventory': inventory,
        'blood_types': blood_types,
    }
    return render(request, 'edit_inventory.html', context)

from django.shortcuts import render
from django.contrib import messages
from .models import Inventory
from .forms import BloodRequestForm

def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            blood_request = form.save()

            # Get the requested blood group and quantity from the form
            requested_blood_group = blood_request.blood_group
            requested_quantity = blood_request.quantity

            # Check availability in the Inventory model
            inventory = Inventory.objects.filter(blood_type=requested_blood_group).first()

            if inventory and inventory.units_available >= requested_quantity:
                # If enough blood is available, show the payment page
                return render(request, 'blood_available.html', {'blood_group': requested_blood_group})
            else:
                # If blood is not available or enough quantity is not available, go to the 'blood_not_availability.html' page
                available_units = inventory.units_available if inventory else 0
                return render(request, 'blood_not_available.html', {
                    'blood_group': requested_blood_group,
                    'available_units': available_units,
                    'requested_units': requested_quantity
                })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BloodRequestForm()

    return render(request, 'request_blood.html', {'form': form})

from django.shortcuts import render
from .models import Registration

from django.shortcuts import render
from .models import Registration

from django.shortcuts import render
from .models import Registration
from django.http import Http404


def recipient_profile(request):
    email = request.session.get('email')

    if email:
        try:
            registration = Registration.objects.get(email=email, role='recipient')
            error = None
        except Registration.DoesNotExist:
            registration = None
            error = 'Profile not found for recipient'
    else:
        registration = None
        error = 'Email not found in session'

    return render(request, 'recipient_profile.html', {
        'registration': registration,
        'error': error
    })


from .forms import RecipientEditForm

def recipient_edit_profile(request):
    email = request.session.get('email')  # Get email from session
    error = None  # Initialize error variable

    if email:
        try:
            # Fetch the recipient's registration based on the email and role
            registration = get_object_or_404(Registration, email=email, role='recipient')
        except Registration.DoesNotExist:
            registration = None
            error = 'Profile not found for recipient'
    else:
        registration = None
        error = 'Email not found in session'

    if request.method == 'POST':
        form = RecipientEditForm(request.POST, instance=registration)  # Bind form with existing data
        if form.is_valid():
            form.save()  # Save the updated registration data
            return redirect('recipient_profile')  # Redirect to the profile view after saving
    else:
        form = RecipientEditForm(instance=registration)  # Pre-fill form with existing data

    return render(request, 'recipient_edit_profile.html', {
        'form': form,
        'error': error  # Always pass the error variable
    })



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Registration
from .forms import ForgotPasswordForm
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.template.loader import render_to_string

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Registration.objects.get(email=email)
                
                # Generate reset token
                reset_token = get_random_string(32)
                user.reset_token = reset_token  # Assuming you have added this field
                user.save()
                
                # Construct the reset link
                reset_link = request.build_absolute_uri(reverse('reset_password', args=[reset_token]))
                
                # Send reset email
                subject = 'Password Reset Request'
                message = f"Click the link to reset your password: {reset_link}"
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')
            except Registration.DoesNotExist:
                messages.error(request, 'No user with that email address found.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password.html', {'form': form})


# views.py
def reset_password(request, token):
    try:
        user = Registration.objects.get(reset_token=token)
    except Registration.DoesNotExist:
        messages.error(request, 'The password reset token is invalid or has expired.')
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user.password = new_password  # Save the password directly without hashing
            user.reset_token = None  # Clear the token
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'reset_password.html', {'user': user})




from django.shortcuts import render, get_object_or_404
from .models import DonorProfile  # Ensure this import matches your app structure

def donor_profile(request):
    donor_id = request.session.get('donor_id')  # Retrieve donor_id from the session

    if donor_id:
        try:
            # Fetch the donor profile based on the donor_id
            donor_profile = DonorProfile.objects.get(donor_id=donor_id)  # Change 'id' to 'donor_id'
            error = None
        except DonorProfile.DoesNotExist:
            donor_profile = None
            error = 'Profile not found for donor'
    else:
        donor_profile = None
        error = 'Donor ID not found in session'

    return render(request, 'donor_profile.html', {
        'donor_profile': donor_profile,
        'error': error
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DonorProfile
from .forms import DonorEditForm  # Ensure this form exists and is configured properly

def donor_edit_profile(request):
    donor_id = request.session.get('donor_id')  # Retrieve donor_id from the session

    if donor_id:
        donor_profile = get_object_or_404(DonorProfile, donor_id=donor_id)  # Fetch donor profile
    else:
        messages.error(request, 'Donor ID not found in session')
        return redirect('donor_dashboard')  # Redirect if donor ID is not found

    if request.method == 'POST':
        form = DonorEditForm(request.POST, instance=donor_profile)  # Bind form with existing data
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, 'Profile updated successfully!')
            return redirect('donor_profile')  # Redirect to the profile view after saving
    else:
        form = DonorEditForm(instance=donor_profile)  # Pre-fill form with existing data

    return render(request, 'donor_edit_profile.html', {
        'form': form,
    })



from django.shortcuts import render
from .models import BloodType, Inventory

def search_blood(request):
    blood_group = request.GET.get('blood_group')
    
    # Fetch the BloodType object that matches the selected blood group
    blood_type = BloodType.objects.filter(blood_group=blood_group).first()
    
    # Check if there is any matching blood type
    if blood_type:
        # Query Inventory where the blood type matches and is_active is True
        available_blood = Inventory.objects.filter(blood_type=blood_type, is_active=True)
    else:
        available_blood = None

    return render(request, 'search_results.html', {'available_blood': available_blood, 'blood_group': blood_group})



# views.py

from django.shortcuts import render, redirect
from .forms import HospitalRequestForm
from .models import Registration

def hospital_request_blood(request):
    if request.method == 'POST':
        form = HospitalRequestForm(request.POST)
        if form.is_valid():
            form.save()  # Automatically saves the user as a recipient
            # Redirect to a success page or hospital dashboard
            return redirect('hospital_dashboard')  # Replace with your success URL
    else:
        form = HospitalRequestForm()

    return render(request, 'hospital_request_blood.html', {'form': form})


from django.shortcuts import render, redirect


def payment_page(request):
    return render(request, 'payment.html')

def payment_success(request):
    return render(request, 'payment_success.html')



from django.shortcuts import render, redirect
from .forms import HospitalRegistrationForm
from .models import Hospital

def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.is_active = True
            hospital.is_approved = False
            hospital.save()
            return redirect('login')  # Redirect to a success page
    else:
        form = HospitalRegistrationForm()
    return render(request, 'hospital_register.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Hospital
from .forms import HospitalLoginForm

def hospital_login(request):
    if request.method == 'POST':
        form = HospitalLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                hospital = Hospital.objects.get(email=email)  # Get the hospital with the provided email
            except Hospital.DoesNotExist:
                messages.error(request, "Invalid email or password")
                return redirect('login')

            # Since you are not using hashed passwords, just compare the raw password
            if password == hospital.password:  # Compare plain-text password
                # Store the hospital ID or any session information
                request.session['hospital_id'] = hospital.hospital_id
                return redirect('hospital_dashboard')  # Redirect to the hospital dashboard on successful login
            else:
                messages.error(request, "Invalid email or password")
                return redirect('login')
    else:
        form = HospitalLoginForm()

    return render(request, 'login.html', {'form': form})



def hospital_dashboard(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_register')  # Redirect to login if not logged in
    
    hospital = Hospital.objects.get(hospital_id=hospital_id)
    return render(request, 'hospital_dashboard.html', {'hospital': hospital})


# views.py

from django.shortcuts import render, redirect
from .forms import DoctorForm

def doctor_register(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()  # Save the doctor to the database
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = DoctorForm()

    return render(request, 'register_doctor.html', {'form': form})


from django.shortcuts import render, redirect
from .forms import DoctorLoginForm
from .models import Doctor


def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Perform authentication by checking email and password
            try:
                # Check if a doctor with the provided email and password exists
                doctor = Doctor.objects.get(email=email, password=password)
                
                # If found, store the doctor_id in the session
                request.session['doctor_id'] = doctor.doctor_id  # Set session for doctor login

                # Redirect to the doctor dashboard
                return redirect('doctor_dashboard')
            except Doctor.DoesNotExist:
                # If no doctor is found, add an error to the form
                form.add_error(None, 'Invalid email or password')
    else:
        form = DoctorLoginForm()

    return render(request, 'login.html', {'form': form})


from django.shortcuts import render, redirect
from .forms import BloodApplyForm
from .models import Doctor

def doctor_dashboard(request):
    # Ensure the doctor is logged in by checking the session
    doctor_id = request.session.get('doctor_id')
    
    if not doctor_id:
        # If not logged in, redirect to the login page
        return redirect('login')

    try:
        # Get the logged-in doctor's profile using 'doctor_id'
        doctor = Doctor.objects.get(doctor_id=doctor_id)  # Correct field name
    except Doctor.DoesNotExist:
        # Handle the case where the doctor does not exist in the database
        return redirect('login')

    # If the form is submitted, process the form data
    if request.method == 'POST':
        blood_apply_form = BloodApplyForm(request.POST)
        if blood_apply_form.is_valid():
            # Save the form, but don't commit yet
            blood_apply = blood_apply_form.save(commit=False)
            # Attach the logged-in doctor to the blood application
            blood_apply.doctor = doctor
            # Now save the blood application with the attached doctor
            blood_apply.save()
            # Redirect to a success page or show a success message
            return redirect('blood_application_success')
    else:
        blood_apply_form = BloodApplyForm()

    # Add the context data for rendering the dashboard and the form
    context = {
        'doctor': doctor,
        'profile': {
            'doctor_name': f"Dr. {doctor.doctor_name}",
            'specialization': doctor.specialization,
            'email': doctor.email,
        },
        'blood_apply_form': blood_apply_form,  # Pass the form to the template
    }

    return render(request, 'doctor_dashboard.html', context)

def blood_application_success(request):
    return render(request, 'blood_application_success.html')




from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DonorRegistrationForm

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')  # Redirect to donor login page after successful registration
    else:
        form = DonorRegistrationForm()

    return render(request, 'register_donor.html', {'form': form})
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from .forms import DonorLoginForm
from .models import DonorProfile

def donor_login(request):
    error_message = None
    if request.method == 'POST':
        form = DonorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                donor = DonorProfile.objects.get(email=email, password=password)
                if donor.is_active:
                    # Store donor ID in session (you can customize this)
                    request.session['donor_id'] = donor.donor_id
                    return redirect('donor_dashboard')  # Redirect to donor dashboard after login
                else:
                    error_message = "Your account is not active. Please contact support."
            except DonorProfile.DoesNotExist:
                error_message = "Invalid email or password. Please try again."
    else:
        form = DonorLoginForm()

    return render(request, 'login.html', {'form': form, 'error_message': error_message})



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Appointment, DonorProfile
from .forms import AppointmentForm
from datetime import timedelta
from django.utils import timezone

def book_appointment(request):
    # Check if the donor is logged in
    if 'donor_id' not in request.session:
        messages.error(request, 'You need to be logged in to book an appointment.')  # Add a message for not logged in
        return redirect('login')  # Redirect to login if not logged in

    donor_id = request.session['donor_id']
    donor = DonorProfile.objects.get(donor_id=donor_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Check if donor can schedule an appointment
            if not donor.can_schedule_appointment():
                messages.error(request, 'You must wait at least 3 months after your last donation before scheduling another appointment.')
                return render(request, 'book_appointment.html', {'form': form, 'donor': donor})  # Stay on the same page

            # Create appointment if valid
            appointment = form.save(commit=False)
            appointment.donor = donor  # Associate appointment with the logged-in donor
            appointment.status = 'Scheduled'  # Set the status to 'Scheduled'
            appointment.save()
            messages.success(request, 'Your appointment has been booked successfully!')
            return redirect('submission_success')  # Redirect to success page
    else:
        form = AppointmentForm()

    return render(request, 'book_appointment.html', {'form': form, 'donor': donor})



from django.shortcuts import redirect, render
from .forms import FirstTimeDonationForm

# View for asking the first-time question
def first_time_donation(request):
    if request.method == 'POST':
        form = FirstTimeDonationForm(request.POST)
        if form.is_valid():
            first_time = form.cleaned_data['first_time_donor']
            if first_time == 'yes':
                return redirect('submit_medical_records')  # Redirect to medical record form
            else:
                return redirect('book_appointment')  # Redirect to appointment booking
    else:
        form = FirstTimeDonationForm()

    return render(request, 'first_time_donation.html', {'form': form})

# View for submitting medical records
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MedicalReportForm
from .models import DonorProfile, MedicalReport

def submit_medical_records(request):
    # Check if the donor is logged in
    if 'donor_id' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    # Get the logged-in donor using the donor_id from the session
    donor_id = request.session['donor_id']
    try:
        donor = DonorProfile.objects.get(donor_id=donor_id)
    except DonorProfile.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor_dashboard')  # Redirect to donor dashboard or another appropriate page

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            medical_report = form.save(commit=False)
            medical_report.donor = donor  # Associate the medical report with the logged-in donor
            medical_report.save()
            messages.success(request, 'Your medical report has been submitted successfully!')
            return redirect('book_appointment')  # Redirect to donor dashboard or a success page
    else:
        form = MedicalReportForm()

    return render(request, 'submit_medical_records.html', {'form': form, 'donor': donor})



def submission_success(request):
    return render(request, 'submission_success.html')  



# blood/views.py
from django.shortcuts import render, redirect
from .forms import BloodApplyWithhospitalForm

def apply_blood(request):
    if request.method == 'POST':
        form = BloodApplyWithhospitalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blood_application_success')  # Redirect to a success page after submission
    else:
        form = BloodApplyWithhospitalForm()
    
    return render(request, 'apply_blood.html', {'blood_apply_form': form})


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DonorProfile

def manage_donors(request):
    donors = DonorProfile.objects.all()  # Get all donors
    return render(request, 'manage_donors.html', {'donors': donors})

def disable_donor(request, donor_id):
    donor = get_object_or_404(DonorProfile, donor_id=donor_id)
    donor.is_active = False
    donor.save()
    messages.success(request, f"{donor.donor_name} has been disabled.")
    return redirect('manage_donors')  # Redirect back to the manage donors page

def enable_donor(request, donor_id):
    donor = get_object_or_404(DonorProfile, donor_id=donor_id)
    donor.is_active = True
    donor.save()
    messages.success(request, f"{donor.donor_name} has been enabled.")
    return redirect('manage_donors')  # Redirect back to the manage donors page


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Doctor

def manage_doctors(request):
    doctors = Doctor.objects.all()  # Get all doctors
    return render(request, 'manage_doctors.html', {'doctors': doctors})

def disable_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    doctor.is_active = False
    doctor.save()
    messages.success(request, f"{doctor.doctor_name} has been disabled.")
    return redirect('manage_doctors')  # Redirect back to the manage doctors page

def enable_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)
    doctor.is_active = True
    doctor.save()
    messages.success(request, f"{doctor.doctor_name} has been enabled.")
    return redirect('manage_doctors')  # Redirect back to the manage doctors page


from django.shortcuts import render, redirect, get_object_or_404
from .models import Hospital

def pending_hospitals(request):
    # Fetch hospitals that are not approved yet
    hospitals = Hospital.objects.filter(is_approved=False)
    return render(request, 'admin_pending_hospitals.html', {'hospitals': hospitals})

def approve_hospital(request, hospital_id):
    # Approve the hospital with the given ID
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)
    hospital.is_approved = True
    hospital.save()
    return redirect('pending_hospitals')
