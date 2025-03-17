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
from django.shortcuts import render
from django.http import HttpResponse
import qrcode
import base64
from io import BytesIO
from .models import DonorProfile

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

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import BloodApply, Inventory

def approve_request(request, request_id):
    # Retrieve the blood request
    blood_request = get_object_or_404(BloodApply, id=request_id)
    
    # Update the request status to approved
    blood_request.status = 'approved'
    blood_request.save()

    # Decrease the available blood units based on the correct field name
    inventory_entry = get_object_or_404(Inventory, blood_type=blood_request.blood_type)
    if inventory_entry.units_available >= blood_request.quantity:
        inventory_entry.units_available -= blood_request.quantity  # Decrease the blood unit count
        inventory_entry.save()

        # Send an email notification to the doctor
        try:
            send_mail(
                subject="Blood Request Approved",
                message=f"Dear Dr. {blood_request.doctor.doctor_name},\n\n"
                        f"Your blood request for {blood_request.blood_type} has been approved and deliver within 1hr.\n"
                        f"Requested Quantity: {blood_request.quantity} units\n"
                        f"Urgency: {blood_request.urgency}\n\n"
                        f"Thank you for using our services.\n\n"
                        f"Best Regards,\nLifeline Blood Bank Team",
                from_email="teenathomas2025@mca.ajce.in",  # Replace with your sender email
                recipient_list=["teenathomasoyr2019@gmail.com"],  # Doctor's email
                fail_silently=False,
            )
            messages.success(request, 'The request has been approved, and a notification email has been sent to the doctor.')
        except Exception as e:
            messages.error(request, f'An error occurred while sending the email: {str(e)}')
    else:
        messages.warning(request, 'Insufficient blood units available. Request cannot be approved.')

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
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
    
    try:
        donor = get_object_or_404(DonorProfile, donor_id=donor_id)
        
        # Get the latest pending request for basic screening
        pending_request = BloodDonationRequest.objects.filter(
            donor=donor,
            status='pending'
        ).order_by('-request_date').first()
        
        context = {
            'donor': donor,
            'pending_request': pending_request
        }
        
        return render(request, 'donor_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('donor_login')
    
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
                user = DonorProfile.objects.get(email=email)
                
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
        user = DonorProfile.objects.get(reset_token=token)
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



from django.shortcuts import render, redirect, get_object_or_404
from .models import Hospital

def hospital_dashboard(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('register_hospital')  # Redirect to login if not logged in
    
    # Fetch the hospital object using 'hospital_id' as the primary key
    hospital = get_object_or_404(Hospital, hospital_id=hospital_id)

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
from django.core.mail import send_mail
from django.contrib import messages
from .forms import BloodApplyForm
from .models import Doctor, BloodApply

def doctor_dashboard(request):
    # Ensure the doctor is logged in by checking the session
    doctor_id = request.session.get('doctor_id')
    
    if not doctor_id:
        return redirect('login')

    try:
        doctor = Doctor.objects.get(doctor_id=doctor_id)
    except Doctor.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        blood_apply_form = BloodApplyForm(request.POST)
        if blood_apply_form.is_valid():
            blood_apply = blood_apply_form.save(commit=False)
            blood_apply.doctor = doctor
            blood_apply.save()

            try:
                # Send a success email to the doctor
                send_mail(
                    subject="Blood Request Submitted Successfully",
                    message=f"Dear Dr. {doctor.doctor_name},\n\n"
                            f"Your blood request for {blood_apply.blood_type} has been successfully submitted.\n"
                            f"Requested Quantity: {blood_apply.quantity} units\n"
                            f"Urgency: {blood_apply.urgency}\n\n"
                            f"Thank you for using our services.\n\n"
                            f"Best Regards,\nLifeline Blood Bank Team",
                    from_email="teenathomas2025@mca.ajce.in",  # Replace with your sender email
                    recipient_list=["teenathomasoyr2019@gmail.com"],  # Send to the doctor's email
                    fail_silently=False,
                )
                messages.success(request, "Your blood request has been submitted successfully. A confirmation email has been sent to you.")
            except Exception as e:
                messages.error(request, f"An error occurred while sending the email: {str(e)}")

            return redirect('blood_application_success')
    else:
        blood_apply_form = BloodApplyForm()

    context = {
        'doctor': doctor,
        'profile': {
            'doctor_name': f"Dr. {doctor.doctor_name}",
            'specialization': doctor.specialization,
            'email': doctor.email,
        },
        'blood_apply_form': blood_apply_form,
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

from django.shortcuts import render, redirect
from .forms import AdminRegistrationForm
from .models import Admin

from django.shortcuts import render, redirect
from .forms import AdminRegistrationForm
from .models import Admin

def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to a login page or another appropriate page
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'aregister.html', {'form': form})






from django.shortcuts import render, redirect
from .models import PlateletsDonation
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def platelets_donation_request(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        blood_type = request.POST.get('blood_type')
        donation_date = request.POST.get('donation_date')
        donation_time = request.POST.get('donation_time')

        # Validate date and time formats
        try:
            donation_date = datetime.strptime(donation_date, '%Y-%m-%d').date()
            donation_time = datetime.strptime(donation_time, '%H:%M').time()
        except ValueError as e:
            logger.error(f"Date or time format error: {e}")
            messages.error(request, 'Invalid date or time format. Please try again.')
            return render(request, 'platelets_donation_form.html')

        # Save the data to the database
        try:
            PlateletsDonation.objects.create(
                name=name,
                email=email,
                phone=phone,
                blood_type=blood_type,
                donation_date=donation_date,
                donation_time=donation_time
            )
            messages.success(request, 'Your platelet donation request has been submitted successfully!')
            return redirect('platelets_donation_status')  # Use the correct URL name
        except Exception as e:
            logger.error(f"Error saving data to the database: {e}")
            messages.error(request, 'An error occurred while saving your request. Please try again later.')
            return render(request, 'platelets_donation_form.html')

    # Render the form for GET requests
    return render(request, 'platelets_donation_form.html')

def platelets_donation_status(request):
    donations = PlateletsDonation.objects.all().order_by('-donation_date')
    return render(request, 'platelets_donation_status.html', {'donations': donations})


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import PlasmaDonation

def plasma_donation_request(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        blood_type = request.POST.get('blood_type')
        donation_date = request.POST.get('donation_date')
        donation_time = request.POST.get('donation_time')

        # Validate required fields
        if not (name and email and phone and blood_type and donation_date and donation_time):
            return render(request, 'plasma_donation_form.html', {
                'error': 'All fields are required. Please fill out the form completely.'
            })

        # Save data to the database
        donation = PlasmaDonation(
            name=name,
            email=email,
            phone=phone,
            blood_type=blood_type,
            donation_date=donation_date,
            donation_time=donation_time
        )
        donation.save()

        # Redirect to a success page or show a success message
        return render(request, 'plasma_sucess.html', {
            'message': 'Thank you for your plasma donation request!'
        })

    # For GET requests, render the form
    return render(request, 'plasma_donation_form.html')


from django.shortcuts import render

def plasma_sucess(request):
    return render(request, 'plasma_sucess.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PlasmaRequest

# View to display all plasma requests
def plasma_requests_page(request):
    plasma_requests = PlasmaRequest.objects.all()
    return render(request, 'plasma_requests_page.html', {'plasma_requests': plasma_requests})

# View to approve a plasma request
def approve_plasma_request(request, request_id):
    try:
        plasma_request = PlasmaRequest.objects.get(id=request_id)
        plasma_request.status = 'approved'  # Update status to 'approved'
        plasma_request.save()  # Save the change
        messages.success(request, 'Plasma request approved successfully.')
    except PlasmaRequest.DoesNotExist:
        messages.error(request, 'Plasma request not found.')

    return redirect('plasma_requests_page')  # Redirect back to the plasma requests page

# View to reject a plasma request
def reject_plasma_request(request, request_id):
    try:
        plasma_request = PlasmaRequest.objects.get(id=request_id)
        plasma_request.status = 'rejected'  # Update status to 'rejected'
        plasma_request.save()  # Save the change
        messages.success(request, 'Plasma request rejected successfully.')
    except PlasmaRequest.DoesNotExist:
        messages.error(request, 'Plasma request not found.')

    return redirect('plasma_requests_page')  # Redirect back to the plasma requests page
# views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .forms import PlasmaRequestForm
from .models import PlasmaRequest, Doctor

def plasma_request_view(request):
    # Ensure the doctor is logged in by checking the session
    doctor_id = request.session.get('doctor_id')
    
    if not doctor_id:
        return redirect('login')

    try:
        doctor = Doctor.objects.get(doctor_id=doctor_id)
    except Doctor.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        plasma_request_form = PlasmaRequestForm(request.POST)
        if plasma_request_form.is_valid():
            plasma_request = plasma_request_form.save(commit=False)
            plasma_request.save()

            try:
                # Send a success email to the doctor
                send_mail(
                    subject="Plasma Request Submitted Successfully",
                    message=f"Dear Dr. {doctor.doctor_name},\n\n"
                            f"Your plasma request for {plasma_request.blood_type} has been successfully submitted.\n"
                            f"Patient Name: {plasma_request.patient_name}\n"
                            f"Requested Quantity: {plasma_request.quantity} units\n"
                            f"Urgency: {plasma_request.urgency}\n\n"
                            f"Thank you for using our services.\n\n"
                            f"Best Regards,\nLifeline Blood Bank Team",
                    from_email="teenathomas2025@mca.ajce.in",  # Replace with your sender email
                    recipient_list=["teenathomasoyr2019@gmail.com"],  # Send to the doctor's email
                    fail_silently=False,
                )
                messages.success(request, "Your plasma request has been submitted successfully. A confirmation email has been sent to you.")
            except Exception as e:
                messages.error(request, f"An error occurred while sending the email: {str(e)}")

            return redirect('plasma_application_success')
    else:
        plasma_request_form = PlasmaRequestForm()

    context = {
        'doctor': doctor,
        'profile': {
            'doctor_name': f"Dr. {doctor.doctor_name}",
            'specialization': doctor.specialization,
            'email': doctor.email,
        },
        'plasma_request_form': plasma_request_form,
    }

    return render(request, 'plasma_request.html', context)

def plasma_application_success(request):
    return render(request, 'plasma_application_success.html')



# views.py
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback, DonorProfile
from .forms import FeedbackForm

def give_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_text = form.cleaned_data['feedback_text']
            
            # Retrieve donor_id from session (ensure this is set during login)
            donor_id = request.session.get('donor_id')  # Replace with actual donor session logic
            
            if donor_id:
                try:
                    # Attempt to retrieve the donor profile
                    donor = DonorProfile.objects.get(donor_id=donor_id)
                    
                    # Create feedback record
                    Feedback.objects.create(donor=donor, feedback_text=feedback_text)
                    
                    # Success message
                    messages.success(request, "Your feedback has been submitted successfully.")
                    return redirect('feedback_success')  # Redirect to success page
                
                except DonorProfile.DoesNotExist:
                    # Handle case where the donor profile doesn't exist
                    messages.error(request, "Donor profile not found. Please contact support.")
                
            else:
                messages.error(request, "You must be logged in to submit feedback.")
                return redirect('login')  # Redirect to login if not logged in
        
        else:
            messages.error(request, "There was an error with your submission. Please try again.")
    
    else:
        form = FeedbackForm()

    return render(request, 'donor_feedback.html', {'form': form})

def feedback_success(request):
    return render(request, 'feedback_success.html')


from django.shortcuts import render
from .models import Feedback  # Assuming you have a Feedback model

def manage_feedback(request):
    feedbacks = Feedback.objects.all()  # Fetch all feedback from the database
    return render(request, 'manage_feedback.html', {'feedbacks': feedbacks})



from datetime import date, timedelta
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from .models import DonorProfile, BloodType

def emergency_alert_page(request):
    if request.method == "POST":
        blood_group_needed = request.POST.get("blood_group")

        # Fetch eligible donors
        eligible_donors = DonorProfile.objects.filter(
            blood_type__blood_group=blood_group_needed,
            is_active=True,
            last_donation_date__lte=date.today() - timedelta(days=90)
        )

        if not eligible_donors.exists():
            return JsonResponse({'status': 'error', 'message': f'No eligible donors found for blood group {blood_group_needed}.'})

        # Send alerts
        for donor in eligible_donors:
            send_mail(
                subject="Urgent: Blood Donation Needed",
                message=f"Dear {donor.donor_name},\n\n"
                        f"There is an urgent need for blood donations of your type ({blood_group_needed}). "
                        "If you are available to donate, please contact us phone no:7568954329.\n\n"
                        "Thank you for your support.\n\n"
                        "Lifeline Blood Bank",
                from_email="teenathomas2025@mca.ajce.in",
                recipient_list=[donor.email],
                fail_silently=False,
            )
        return JsonResponse({'status': 'success', 'message': f'Alerts sent for blood group {blood_group_needed}.'})

    # Get all blood types for the dropdown
    blood_types = BloodType.objects.all()
    return render(request, "emergency_alert.html", {"blood_types": blood_types})


from django.shortcuts import render, redirect
from .models import Appointment

def manage_appointments(request):
    appointments = Appointment.objects.select_related("donor").all()  # Fetch appointments with donor details

    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = new_status
        appointment.save()

        return redirect("manage_appointments")  # Reload the page after updating

    return render(request, "manage_appointments.html", {"appointments": appointments})


from django.shortcuts import render, get_object_or_404
from .models import BloodApply, Inventory, Hospital  # Removed unnecessary Doctor import

def hospital_report(request, hospital_id):
    hospital = get_object_or_404(Hospital, pk=hospital_id)

    # Get all blood requests by this hospital, including doctor details
    blood_requests = BloodApply.objects.select_related('doctor', 'blood_type').filter(hospital=hospital)

    # Count requests by status
    total_requests = blood_requests.count()
    pending_count = blood_requests.filter(status='pending').count()
    approved_count = blood_requests.filter(status='approved').count()
    fulfilled_count = blood_requests.filter(status='fulfilled').count()
    rejected_count = blood_requests.filter(status='rejected').count()

    # Urgency breakdown
    normal_count = blood_requests.filter(urgency='normal').count()
    emergency_count = blood_requests.filter(urgency='emergency').count()

    # Available Blood Inventory (filtered by hospital, if applicable)
    blood_inventory = Inventory.objects.all()

    context = {
        'hospital': hospital,
        'blood_requests': blood_requests,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'fulfilled_count': fulfilled_count,
        'rejected_count': rejected_count,
        'normal_count': normal_count,
        'emergency_count': emergency_count,
        'blood_inventory': blood_inventory,
    }
    return render(request, 'hospital_report.html', context)


from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from .models import Hospital, BloodApply

def download_hospital_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="hospital_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y_position = height - 50  # Start position

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y_position, "Hospital Blood Request Report")
    y_position -= 40  # Space after title

    hospitals = Hospital.objects.all()

    for hospital in hospitals:
        if y_position < 200:  # Create a new page if space is low
            p.showPage()
            p.setFont("Helvetica", 12)
            y_position = height - 50  # Reset position

        # Fetch hospital blood requests
        blood_requests = BloodApply.objects.filter(hospital=hospital)

        # Count request statuses
        total_requests = blood_requests.count()
        pending_requests = blood_requests.filter(status="pending").count()
        approved_requests = blood_requests.filter(status="approved").count()
        emergency_requests = blood_requests.filter(urgency="emergency").count()

        # Hospital Info
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, f"Hospital: {hospital.hospital_name}")
        p.setFont("Helvetica", 12)
        p.drawString(50, y_position - 20, f"Phone: {hospital.phone_number}  |  Email: {hospital.email}")
        p.drawString(50, y_position - 40, f"Total Requests: {total_requests}, Pending: {pending_requests}, Approved: {approved_requests}, Emergency: {emergency_requests}")
        
        y_position -= 60  # Space after hospital info

        # Table Headers
        data = [
            ["Blood Type", "Quantity", "Urgency", "Status", "Patient Name", "Patient Age", "Reason"]
        ]

        # Table Data
        for request in blood_requests:
            data.append([
                request.blood_type.blood_group,
                request.quantity,
                request.urgency.capitalize() if request.urgency else "-",
                request.status.capitalize(),
                request.patient_name if request.patient_name else "-",
                request.patient_age if request.patient_age else "-",
                request.reason if request.reason else "-"
            ])

        # Define Table Style
        table = Table(data, colWidths=[80, 60, 60, 80, 100, 60, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Draw Table
        table.wrapOn(p, width, height)
        table.drawOn(p, 50, y_position - (len(data) * 20))  # Adjust Y position dynamically

        y_position -= (len(data) * 20) + 40  # Space after table

        if y_position < 200:  # If space is low, start a new page
            p.showPage()
            y_position = height - 50

    p.showPage()
    p.save()

    return response



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DonorProfile, BloodDonationRequest
from datetime import datetime, timedelta

def request_blood_donation(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
        
    donor_profile = get_object_or_404(DonorProfile, donor_id=donor_id)
    
    # Check for pending requests
    if BloodDonationRequest.objects.filter(donor=donor_profile, status='pending').exists():
        messages.warning(request, 'You already have a pending donation request.')
        return redirect('donation_history')
    
    if request.method == 'POST':
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        
        # Create donation request
        donation_request = BloodDonationRequest.objects.create(
            donor=donor_profile,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            status='pending'
        )
        
        messages.success(request, 'Your donation request has been submitted successfully!')
        return redirect('donation_steps')
        
    return render(request, 'request_donation.html', {
        'donor': donor_profile,
        'today': datetime.now().date()
    })

def donation_steps(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
        
    donor_profile = get_object_or_404(DonorProfile, donor_id=donor_id)
    
    try:
        donation_request = BloodDonationRequest.objects.get(
            donor=donor_profile, 
            status='pending'
        )
    except BloodDonationRequest.DoesNotExist:
        messages.warning(request, 'No pending donation request found.')
        return redirect('donor_dashboard')
    
    return render(request, 'donation_steps.html', {
        'donor': donor_profile,
        'donation_request': donation_request
    })

def donor_donation_history(request):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
        
    donor_profile = get_object_or_404(DonorProfile, donor_id=donor_id)
    donation_requests = BloodDonationRequest.objects.filter(
        donor=donor_profile
    ).order_by('-request_date')
    
    return render(request, 'donation_history.html', {
        'donor': donor_profile,
        'donation_requests': donation_requests
    })

def cancel_donation(request, request_id):
    # Get donor_id from session
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
    
    try:
        # Get the donation request
        donation_request = get_object_or_404(
            BloodDonationRequest, 
            id=request_id,
            donor__donor_id=donor_id,
            status='pending'
        )
        
        # Update the donation request
        donation_request.status = 'cancelled'
        donation_request.notes = 'Cancelled by donor'
        donation_request.save()
        
        messages.success(request, 'Donation request cancelled successfully.')
        
    except BloodDonationRequest.DoesNotExist:
        messages.error(request, 'Donation request not found or cannot be cancelled.')
    except Exception as e:
        messages.error(request, f'Error cancelling donation: {str(e)}')
    
    return redirect('donation_history')
def reschedule_donation(request, request_id):
    donation_request = get_object_or_404(
        BloodDonationRequest, 
        id=request_id,
        donor__donor_id=donor_id
    )
    
    if request.method == 'POST':
        if donation_request.status == 'pending':
            new_date = request.POST.get('preferred_date')
            new_time = request.POST.get('preferred_time')
            
            donation_request.preferred_date = new_date
            donation_request.preferred_time = new_time
            donation_request.notes = 'Rescheduled by donor'
            donation_request.save()
            
            messages.success(request, 'Donation request rescheduled successfully.')
            return redirect('donation_history')
        else:
            messages.error(request, 'Cannot reschedule this donation request.')
    
    return render(request, 'blood/reschedule_donation.html', {
        'donation_request': donation_request,
        'today': datetime.now().date()
    })

from .models import BloodDonationRequest, BasicScreening
from decimal import Decimal


def basic_screening(request, request_id):
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
        
    donation_request = get_object_or_404(
        BloodDonationRequest, 
        id=request_id,
        donor__donor_id=donor_id
    )
    
    # Check if screening already exists
    if BasicScreening.objects.filter(donation_request=donation_request).exists():
        messages.warning(request, 'Screening already completed for this donation request')
        return redirect('donation_history')
    
    if request.method == 'POST':
        try:
            blood_pressure = request.POST.get('blood_pressure')
            temperature = Decimal(request.POST.get('temperature'))
            weight = Decimal(request.POST.get('weight'))
            pulse_rate = int(request.POST.get('pulse_rate'))
            hemoglobin = Decimal(request.POST.get('hemoglobin'))
            notes = request.POST.get('notes')

            # Basic eligibility checks
            is_eligible = True
            messages_list = []

            # Weight check
            if weight < 50:
                is_eligible = False
                messages_list.append("Weight must be at least 50 kg")

            # Temperature check
            if temperature > 37.5:
                is_eligible = False
                messages_list.append("Temperature is above normal range")

            # Blood pressure check
            try:
                systolic, diastolic = map(int, blood_pressure.split('/'))
                if systolic < 90 or systolic > 180 or diastolic < 60 or diastolic > 100:
                    is_eligible = False
                    messages_list.append("Blood pressure is out of normal range")
            except ValueError:
                messages.error(request, "Invalid blood pressure format. Use format like '120/80'")
                return render(request, 'blood/basic_screening.html', {'donation_request': donation_request})

            # Create screening record
            BasicScreening.objects.create(
                donation_request=donation_request,
                blood_pressure=blood_pressure,
                temperature=temperature,
                weight=weight,
                pulse_rate=pulse_rate,
                hemoglobin=hemoglobin,
                is_eligible=is_eligible,
                notes=notes
            )

            if is_eligible:
                donation_request.status = 'approved'
                donation_request.save()
                messages.success(request, 'Basic screening completed successfully!')
            else:
                donation_request.status = 'cancelled'
                donation_request.save()
                for msg in messages_list:
                    messages.error(request, msg)

            return redirect('donation_history')
            
        except ValueError as e:
            messages.error(request, f'Please enter valid numerical values: {str(e)}')
            
    return render(request, 'basic_screening.html', {
        'donation_request': donation_request
    })
def reschedule_donation(request, request_id):
    # Get donor_id from session
    donor_id = request.session.get('donor_id')
    if not donor_id:
        messages.error(request, 'Please login first')
        return redirect('donor_login')
    
    # Get the donation request
    donation_request = get_object_or_404(
        BloodDonationRequest, 
        id=request_id,
        donor__donor_id=donor_id,
        status='pending'
    )
    
    if request.method == 'POST':
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        
        if preferred_date and preferred_time:
            try:
                # Update the donation request
                donation_request.preferred_date = preferred_date
                donation_request.preferred_time = preferred_time
                donation_request.notes = 'Rescheduled by donor'
                donation_request.save()
                
                messages.success(request, 'Donation request rescheduled successfully.')
                return redirect('donation_history')
            except Exception as e:
                messages.error(request, f'Error rescheduling donation: {str(e)}')
        else:
            messages.error(request, 'Please provide both date and time.')
    
    # For GET request, show the reschedule form
    context = {
        'donation_request': donation_request,
        'today': datetime.now().date()
    }
    return render(request, 'reschedule_donation.html', context)

def manage_donation_requests(request):
    try:
        # Get all donation requests ordered by date
        donation_requests = BloodDonationRequest.objects.all().order_by('-request_date')
        
        context = {
            'donation_requests': donation_requests
        }
        
        return render(request, 'manage_donation_requests.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('blood_admin')

def update_donation_status(request, request_id):
    try:
        # Get the donation request
        donation_request = get_object_or_404(BloodDonationRequest, id=request_id)
        
        if request.method == 'POST':
            new_status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            # Validate the status
            if new_status in ['pending', 'approved', 'completed', 'cancelled']:
                # Update the status
                donation_request.status = new_status
                donation_request.notes = notes
                
                # If marking as completed, update completion date
                if new_status == 'completed':
                    donation_request.completion_date = datetime.now()
                    # Update donor's last donation date
                    donor = donation_request.donor
                    donor.last_donation_date = datetime.now().date()
                    donor.save()
                
                donation_request.save()
                messages.success(request, 'Status updated successfully')
            else:
                messages.error(request, 'Invalid status')
                
        return render(request, 'update_donation_status.html', {
            'donation_request': donation_request
        })
        
    except Exception as e:
        messages.error(request, f'Error updating status: {str(e)}')
        return redirect('manage_donation_requests')
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BloodTest, BloodDonationRequest
from datetime import datetime

def apply_test(request, donation_id):
    donation = get_object_or_404(BloodDonationRequest, id=donation_id)
    
    # Check if test already exists
    existing_test = BloodTest.objects.filter(donation=donation).first()
    if existing_test:
        messages.warning(request, 'Blood test already exists for this donation')
        return redirect('view_test', test_id=existing_test.id)
    
    if request.method == 'POST':
        try:
            blood_test = BloodTest(
                donation=donation,
                hiv=request.POST.get('hiv', False) == 'on',
                hepatitis_b=request.POST.get('hepatitis_b', False) == 'on',
                hepatitis_c=request.POST.get('hepatitis_c', False) == 'on',
                syphilis=request.POST.get('syphilis', False) == 'on',
                malaria=request.POST.get('malaria', False) == 'on',
                hemoglobin=float(request.POST.get('hemoglobin')),
                tested_by=request.POST.get('tested_by'),
                remarks=request.POST.get('remarks', '')
            )
            blood_test.save()
            blood_test.check_safety()
            
            messages.success(request, 'Blood test results recorded successfully')
            return redirect('view_test', test_id=blood_test.id)
            
        except Exception as e:
            messages.error(request, f'Error recording test results: {str(e)}')
    
    return render(request, 'apply_test.html', {
        'donation': donation
    })

def view_test(request, test_id):
    blood_test = get_object_or_404(BloodTest, id=test_id)
    return render(request, 'view_test.html', {
        'blood_test': blood_test
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BloodTest, BloodDonationRequest

def test_list(request):
    # Debug prints
    print("Session data:", request.session.items())
    print("Donor ID:", request.session.get('donor_id'))
    print("Donor Name:", request.session.get('donor_name'))

    if 'donor_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('donor_login')

    try:
        donor_id = request.session.get('donor_id')
        
        # Get all tests for this donor
        blood_tests = BloodTest.objects.filter(
            donation__donor__donor_id=donor_id
        ).order_by('-test_date')
        
        # Debug print
        print(f"Found {blood_tests.count()} tests for donor {donor_id}")
        
        context = {
            'blood_tests': blood_tests,
        }
        
        return render(request, 'test_list.html', context)
        
    except Exception as e:
        print(f"Error in test_list: {str(e)}")
        messages.error(request, f'Error loading test list: {str(e)}')
        return redirect('donor_login')

def pending_test(request):
    # Debug prints
    print("Session data:", request.session.items())
    print("Donor ID:", request.session.get('donor_id'))

    if 'donor_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('donor_login')

    try:
        donor_id = request.session.get('donor_id')
        
        # Get pending donations for this donor
        pending_donations = BloodDonationRequest.objects.filter(
            donor__donor_id=donor_id,
            status='approved'
        ).exclude(
            bloodtest__isnull=False
        ).order_by('request_date')
        
        # Debug print
        print(f"Found {pending_donations.count()} pending donations for donor {donor_id}")
        
        context = {
            'pending_donations': pending_donations,
        }
        
        return render(request, 'pending_test.html', context)
        
    except Exception as e:
        print(f"Error in pending_test: {str(e)}")
        messages.error(request, f'Error loading pending tests: {str(e)}')
        return redirect('donor_login')
    
        
def print_test(request, test_id):
    blood_test = get_object_or_404(BloodTest, id=test_id)
    return render(request, 'print_test.html', {
        'blood_test': blood_test
    })


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DonorProfile

def change_password(request):
    # Check if donor is logged in via session
    donor_id = request.session.get('donor_id')
    
    if not donor_id:
        messages.error(request, 'Please login to change password')
        return redirect('login')
    
    try:
        # Get the donor profile
        donor = DonorProfile.objects.get(donor_id=donor_id)

        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Check if current password is correct
            if donor.password != old_password:
                messages.error(request, 'Current password is incorrect')
                return redirect('change_password')

            # Validate new password
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return redirect('change_password')

            if len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters long')
                return redirect('change_password')

            # Update password
            donor.password = new_password
            donor.save()
            
            messages.success(request, 'Password changed successfully')
            return redirect('donor_profile')

        return render(request, 'change_password.html')

    except DonorProfile.DoesNotExist:
        messages.error(request, 'Donor profile not found')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')
    
    
    
from django.shortcuts import render
from .models import BloodTest, DonorProfile

def admin_test_list(request):
    donor_name = request.GET.get('donor_name', '')
    
    if donor_name:
        # Find the donor by donor_name
        donors = DonorProfile.objects.filter(donor_name__icontains=donor_name)
        # Find donations for these donors
        donations = BloodDonationRequest.objects.filter(donor__in=donors)
        # Get tests for these donations
        tests = BloodTest.objects.filter(donation__in=donations).order_by('-test_date')
    else:
        tests = BloodTest.objects.all().order_by('-test_date')
    
    context = {
        'tests': tests,
        'donor_name': donor_name
    }
    return render(request, 'admin_donor_tests.html', context)



import requests
from django.shortcuts import render
from blood.models import Campaign

def get_coordinates(location):
    """Fetch latitude & longitude using OpenStreetMap API"""
    api_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "LifelineBloodBank/1.0 (contact@example.com)"  # Replace with your email
    }

    response = requests.get(api_url, params=params, headers=headers)
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"])
    
    return None, None  # Return None if API fails

def blood_camp_locator(request):
    """Fetch campaigns and add coordinates dynamically"""
    campaigns = Campaign.objects.all()
    campaign_data = []

    for camp in campaigns:
        lat, lon = get_coordinates(camp.location)
        if lat and lon:
            campaign_data.append({
                "name": camp.name,
                "lat": lat,
                "lon": lon,
                "description": camp.description
            })

    return render(request, "camp_locator.html", {"campaign_data": campaign_data})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BloodApply, DonorProfile, DonorRecipientMatch
from .ml_matching import MLMatchingSystem
from datetime import datetime, timedelta

def find_matches(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        try:
            blood_request = BloodApply.objects.get(id=request_id)
            matching_system = MLMatchingSystem()
            
            eligible_donors = DonorProfile.objects.filter(
                is_active=True,
                blood_type__isnull=False
            ).exclude(
                last_donation_date__gte=datetime.now().date() - timedelta(days=90)
            )
            
            matches = []
            for donor in eligible_donors:
                ml_score = matching_system.predict_match_score(blood_request, donor)
                
                if ml_score > 0.5:
                    match = DonorRecipientMatch.objects.create(
                        blood_request=blood_request,
                        donor=donor,
                        match_score=ml_score * 100,  # Convert to percentage
                        ml_confidence=ml_score
                    )
                    matches.append(match)
            
            if matches:
                messages.success(request, f"Found {len(matches)} potential donors!")
            else:
                messages.warning(request, "No suitable donors found at this time.")
                
            return render(request, 'matching_results.html', {
                'matches': matches,
                'blood_request': blood_request
            })
            
        except BloodApply.DoesNotExist:
            messages.error(request, "Blood request not found!")
            return redirect('find_matches')
    
    return render(request, 'find_matches.html')
def match_details(request, match_id):
    try:
        match = DonorRecipientMatch.objects.get(id=match_id)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                match.status = 'accepted'
                match.save()
                messages.success(request, 'Match accepted successfully!')
            elif action == 'reject':
                match.status = 'rejected'
                match.save()
                messages.success(request, 'Match rejected successfully!')
                
        return render(request, 'match_details.html', {'match': match})
    except DonorRecipientMatch.DoesNotExist:
        messages.error(request, "Match not found!")
        return redirect('find_matches')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import (
    Hospital, 
    BloodType, 
    BloodDemandPrediction,
    DemandHistory
)
from datetime import datetime, timedelta
import random

def predict_demand(request):
    print("View called")  # Debug print
    
    # For GET request - show the form
    hospitals = Hospital.objects.all()  # Get all hospitals, not just active ones
    blood_types = BloodType.objects.all()
    
    print(f"Found {hospitals.count()} hospitals and {blood_types.count()} blood types")  # Debug print
    
    if request.method == 'POST':
        try:
            hospital_id = request.POST.get('hospital')
            blood_type_id = request.POST.get('blood_type')
            days = int(request.POST.get('days', 30))
            
            print(f"POST data: hospital={hospital_id}, blood_type={blood_type_id}, days={days}")  # Debug print
            
            # Get the hospital and blood type
            hospital = Hospital.objects.get(hospital_id=hospital_id)
            blood_type = BloodType.objects.get(blood_group=blood_type_id)
            
            # Generate predictions
            predictions = []
            start_date = datetime.now().date()
            
            for i in range(days):
                pred_date = start_date + timedelta(days=i)
                
                # Generate demand based on blood type
                base_demand = {
                    'A+': random.randint(8, 15),
                    'A-': random.randint(5, 10),
                    'B+': random.randint(7, 12),
                    'B-': random.randint(4, 8),
                    'O+': random.randint(10, 18),
                    'O-': random.randint(6, 12),
                    'AB+': random.randint(3, 7),
                    'AB-': random.randint(2, 5),
                }.get(blood_type.blood_group, 10)
                
                predicted_demand = base_demand
                confidence_score = random.uniform(75, 95)  # 75% to 95% confidence
                
                prediction = BloodDemandPrediction.objects.create(
                    hospital=hospital,
                    blood_type=blood_type,
                    prediction_date=pred_date,
                    predicted_demand=predicted_demand,
                    confidence_score=confidence_score
                )
                predictions.append(prediction)
            
            # Calculate statistics
            total_demand = sum(p.predicted_demand for p in predictions)
            avg_demand = total_demand / len(predictions)
            min_demand = min(p.predicted_demand for p in predictions)
            max_demand = max(p.predicted_demand for p in predictions)
            
            # Generate seasonal patterns
            seasonal_pattern = {
                'Winter': random.randint(8, 12),
                'Spring': random.randint(10, 15),
                'Summer': random.randint(12, 18),
                'Fall': random.randint(9, 14)
            }
            
            # Generate holiday impact
            holiday_impact = {
                0: random.randint(8, 12),  # Regular days
                1: random.randint(15, 20)   # Holidays
            }
            
            return render(request, 'demand_prediction.html', {
                'predictions': predictions,
                'seasonal_pattern': seasonal_pattern,
                'holiday_impact': holiday_impact,
                'hospital': hospital,
                'blood_type': blood_type,
                'days': days,
                'total_demand': total_demand,
                'avg_demand': avg_demand,
                'min_demand': min_demand,
                'max_demand': max_demand
            })
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug print
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'predict_demand_form.html', {
                'hospitals': hospitals,
                'blood_types': blood_types,
                'error': str(e)
            })
    
    # Render the form template
    return render(request, 'predict_demand_form.html', {
        'hospitals': hospitals,
        'blood_types': blood_types
    })



def show_campaign_success(request, campaign_id):
    try:
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
        
        # Calculate duration
        duration = (campaign.end_date - campaign.start_date).days + 1

        # Calculate estimated donors
        donors_per_day = {
            'Urban': 35,
            'Suburban': 25,
            'Rural': 15
        }.get(campaign.location, 25)
        
        estimated_donors = duration * donors_per_day

        # Calculate resources
        resources = {
            'Staff Required': max(3, int(estimated_donors / (duration * 20))),
            'Beds Needed': max(2, int(estimated_donors / (duration * 15))),
            'Needles': int(estimated_donors * 1.2),
            'Cotton Swabs': int(estimated_donors * 3),
            'Blood Bags': int(estimated_donors * 1.1),
            'Antiseptic (liters)': max(1, int(estimated_donors * 0.05)),
            'Gloves (pairs)': int(estimated_donors * 2),
            'Bandages': int(estimated_donors * 1.2)
        }

        # Calculate costs
        costs = {
            'Staff Cost': resources['Staff Required'] * duration * 1200,
            'Needles Cost': resources['Needles'] * 15,
            'Cotton Cost': resources['Cotton Swabs'] * 5,
            'Blood Bags Cost': resources['Blood Bags'] * 350,
            'Antiseptic Cost': resources['Antiseptic (liters)'] * 200,
            'Gloves Cost': resources['Gloves (pairs)'] * 25,
            'Bandages Cost': resources['Bandages'] * 10,
            'Refreshments': estimated_donors * 50,
            'Miscellaneous': estimated_donors * 20
        }

        # Format costs with Indian number system
        def format_indian_currency(amount):
            s = str(amount)
            l = len(s)
            if l > 3:
                i = l - 3
                while i > 0:
                    s = s[:i] + ',' + s[i:]
                    i -= 2
            return s

        formatted_costs = {k: format_indian_currency(v) for k, v in costs.items()}
        total_cost = format_indian_currency(sum(costs.values()))

        # Calculate success rate
        base_success_rate = 75
        location_bonus = {'Urban': 10, 'Suburban': 5, 'Rural': 0}.get(campaign.location, 5)
        duration_bonus = min(15, duration/7 * 2)
        success_rate = min(100, base_success_rate + location_bonus + duration_bonus)

        context = {
            'campaign': campaign,
            'success_rate': round(success_rate, 1),
            'estimated_donors': estimated_donors,
            'duration': duration,
            'location_type': campaign.location,
            'resources': resources,
            'costs': formatted_costs,
            'total_cost': total_cost
        }
        
        return render(request, 'predict_campaign_success.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('latest_campaigns')
    
    
from django.shortcuts import render
from .models import DonorProfile  # Change from Donor to DonorProfile
from .health_risk_assessment import HealthRiskAnalyzer

def donor_health_list(request):
    donors = DonorProfile.objects.all().order_by('donor_name')  # Changed from name to donor_name
    return render(request, 'donor_health_list.html', {'donors': donors})

def assess_donor_health(request, donor_id):
    try:
        donor = DonorProfile.objects.get(donor_id=donor_id)  # Changed from id to donor_id
        analyzer = HealthRiskAnalyzer()
        
        # Perform risk assessment
        risk_assessment = analyzer.assess_risk(donor)
        
        context = {
            'donor': donor,
            'risk_assessment': risk_assessment,
            'risk_factors': risk_assessment['risk_factors'],
            'recommendations': risk_assessment['recommendations']
        }
        
        return render(request, 'health_risk_assessment.html', context)
        
    except DonorProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Donor not found'})
    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})

from django.shortcuts import render
from .models import DonorProfile
from .health_risk_assessment import HealthRiskAnalyzer

def health_risk_view(request):
    try:
        donors = DonorProfile.objects.all().order_by('donor_name')
        
        if request.method == 'POST':
            donor_id = request.POST.get('donor_id')
            
            # Add validation for empty donor_id
            if not donor_id:
                return render(request, 'health_risk.html', {
                    'donors': donors,
                    'error': 'Please select a donor.'
                })
                
            try:
                # Convert donor_id to integer
                donor_id = int(donor_id)
                donor = DonorProfile.objects.get(donor_id=donor_id)
                analyzer = HealthRiskAnalyzer()
                risk_assessment = analyzer.assess_risk(donor)
                
                context = {
                    'donors': donors,
                    'selected_donor': donor,
                    'risk_assessment': risk_assessment,
                    'risk_factors': risk_assessment['risk_factors'],
                    'recommendations': risk_assessment['recommendations'],
                    'donor_points': risk_assessment['donor_points'],
                    'age': risk_assessment['age'],
                    'next_eligible_date': risk_assessment['next_eligible_date']
                }
                
                return render(request, 'health_risk.html', context)
                
            except (ValueError, DonorProfile.DoesNotExist):
                return render(request, 'health_risk.html', {
                    'donors': donors,
                    'error': 'Invalid donor selection.'
                })
        
        # For GET request, just show the form
        return render(request, 'health_risk.html', {
            'donors': donors
        })
        
    except Exception as e:
        return render(request, 'health_risk.html', {
            'error': str(e)
        })
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Hospital, BloodType, BloodTransfer
from django.utils import timezone

def inter_hospital_request(request):
    if 'hospital_id' not in request.session:
        return redirect('hospital_login')
    
    requesting_hospital = Hospital.objects.get(hospital_id=request.session['hospital_id'])
    
    if request.method == 'POST':
        to_hospital_id = request.POST.get('to_hospital')
        blood_type_id = request.POST.get('blood_type')
        units = request.POST.get('units')
        priority = request.POST.get('priority')
        notes = request.POST.get('notes')
        
        try:
            transfer = BloodTransfer.objects.create(
                from_hospital=requesting_hospital,
                to_hospital_id=to_hospital_id,
                blood_type_id=blood_type_id,
                units=units,
                priority=priority,
                notes=notes,
                status='pending'
            )
            messages.success(request, 'Inter-hospital blood request sent successfully')
            return redirect('hospital_requests')
        except Exception as e:
            messages.error(request, str(e))
    
    hospitals = Hospital.objects.exclude(hospital_id=requesting_hospital.hospital_id)
    blood_types = BloodType.objects.all()
    
    return render(request, 'inter_hospital_request.html', {
        'hospitals': hospitals,
        'blood_types': blood_types
    })

def hospital_requests(request):
    if 'hospital_id' not in request.session:
        return redirect('hospital_login')
    
    hospital = Hospital.objects.get(hospital_id=request.session['hospital_id'])
    
    sent_requests = BloodTransfer.objects.filter(from_hospital=hospital)
    received_requests = BloodTransfer.objects.filter(to_hospital=hospital)
    
    return render(request, 'hospital_requests.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })


def process_request(request, transfer_id):
    if 'hospital_id' not in request.session:
        return redirect('hospital_login')
    
    transfer = get_object_or_404(BloodTransfer, transfer_id=transfer_id)
    hospital = Hospital.objects.get(hospital_id=request.session['hospital_id'])
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            transfer.status = 'approved'
            transfer.approval_date = timezone.now()
            transfer.save()
            
            request.session['alert_message'] = {
                'type': 'success',
                'message': f"Blood request from {transfer.from_hospital.hospital_name} for {transfer.units} units of {transfer.blood_type} has been accepted",
                'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            messages.success(request, 'Request accepted successfully')
                
        elif action == 'reject':
            transfer.status = 'cancelled'
            transfer.save()
            
            request.session['alert_message'] = {
                'type': 'danger',
                'message': f"Blood request rejected",
                'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            messages.success(request, 'Blood request rejected')

        elif action == 'deliver':
            transfer.status = 'delivered'
            transfer.delivery_date = timezone.now()
            transfer.save()
            
            request.session['alert_message'] = {
                'type': 'success',
                'message': f"Blood transfer of {transfer.units} units of {transfer.blood_type} has been delivered",
                'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            messages.success(request, 'Blood transfer marked as delivered')
    
    return redirect('hospital_requests')

from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
import qrcode
import base64
from io import BytesIO
from .models import DonorProfile

def donor_card(request):
    try:
        # Get donor_id from session
        donor_id = request.session.get('donor_id')
        if not donor_id:
            return HttpResponse("Please login first", status=401)
            
        donor = DonorProfile.objects.get(donor_id=donor_id)
        
        # Calculate age from date_of_birth
        today = datetime.now()
        age = today.year - donor.date_of_birth.year - ((today.month, today.day) < (donor.date_of_birth.month, donor.date_of_birth.day))
        
        # Calculate next eligible donation date
        next_donation_date = None
        if donor.last_donation_date:
            next_donation_date = donor.last_donation_date + timedelta(days=90)
        
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = (
            f"Donor ID: {donor.donor_id}\n"
            f"Name: {donor.donor_name}\n"
            f"Blood Group: {donor.blood_type}\n"
            f"Contact: {donor.contact_number}\n"
            f"Email: {donor.email}"
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 string
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'donor': donor,
            'age': age,
            'qr_code': qr_code,
            'organization_name': 'Blood Bank Management System',
            'next_donation_date': next_donation_date,
            'points': donor.points,
            'valid_until': (datetime.now() + timedelta(days=365)).date()
        }
        
        return render(request, 'donor_card.html', context)
        
    except DonorProfile.DoesNotExist:
        return HttpResponse("Donor not found", status=404)
    
# blood/views.py
from django.shortcuts import render
from .models import DonorProfile, BloodRequest
from .donor_prediction import DonorAvailabilityPredictor

# Initialize the predictor
predictor = DonorAvailabilityPredictor()

def train_donor_predictor():
    """
    Function to train the donor prediction model
    Can be called from views or wherever needed
    """
    predictor = DonorAvailabilityPredictor()
    
    # Train the model
    accuracy = predictor.train_model()
    return accuracy

# blood/views.py
from django.shortcuts import render, get_object_or_404
from .models import DonorProfile, BloodRequest
from .donor_prediction import DonorAvailabilityPredictor

# Initialize the predictor
predictor = DonorAvailabilityPredictor()

def find_available_donors(request, blood_request_id):
    # Use get_object_or_404 to handle non-existent BloodRequest
    blood_request = get_object_or_404(BloodRequest, id=blood_request_id)
    
    matching_donors = DonorProfile.objects.filter(
        blood_type=blood_request.blood_type,
        is_active=True
    )
    
    available_donors = []
    for donor in matching_donors:
        prediction = predictor.predict_availability(donor)
        if prediction['is_available']:
            donor.availability_probability = prediction['probability']
            available_donors.append(donor)
    
    # Sort donors by availability probability
    available_donors.sort(key=lambda x: x.availability_probability, reverse=True)
    
    return render(request, 'available_donors.html', {
        'blood_request': blood_request,
        'available_donors': available_donors
    })

def some_view(request):
    # Train the model when needed
    accuracy = train_donor_predictor()
    # Use the trained model for predictions
    # ... rest of your view logic

# blood/views.py
# blood/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DonorProfile, DonorIronStatus, BloodType
from .ai_model import IronStatusPredictor

# Initialize the AI predictor
predictor = IronStatusPredictor()

def donor_iron_status_list(request):
    """Display iron status for the logged-in donor with AI predictions"""
    # Debug prints
    print("Session data:", request.session.items())
    print("Donor ID:", request.session.get('donor_id'))
    print("Donor Name:", request.session.get('donor_name'))

    if 'donor_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('donor_login')

    try:
        donor_id = request.session.get('donor_id')
        
        # Get iron status for the logged-in donor only
        iron_status_list = DonorIronStatus.objects.filter(
            donor__donor_id=donor_id
        ).select_related('donor')
        
        # Debug print
        print(f"Found {iron_status_list.count()} iron status records for donor {donor_id}")
        
        # Process donor's data with AI
        donors_data = []
        for status in iron_status_list:
            features = [
                status.hemoglobin_level,
                status.serum_ferritin,
                status.transferrin_saturation_index,
                status.total_iron_binding_capacity,
                status.donation_count_last_year
            ]
            
            predicted_status = predictor.predict(features)
            diet_recommendation = predictor.get_diet_recommendation(predicted_status)
            
            donors_data.append({
                'donor_name': status.donor.donor_name,
                'blood_type': status.donor.blood_type,
                'current_status': status.iron_deficiency_status,
                'predicted_status': predicted_status,
                'hemoglobin': status.hemoglobin_level,
                'ferritin': status.serum_ferritin,
                'tsi': status.transferrin_saturation_index,
                'tibc': status.total_iron_binding_capacity,
                'donations': status.donation_count_last_year,
                'diet_recommendation': diet_recommendation,
                'last_donation_date': status.donor.last_donation_date,
                'contact': status.donor.contact_number,
                'email': status.donor.email,
                'points': status.donor.points
            })

        context = {
            'donors_data': donors_data,
            'donor_name': request.session.get('donor_name')
        }
        
        return render(request, 'all_donors_iron_status.html', context)
        
    except Exception as e:
        print(f"Error in iron status list: {str(e)}")
        messages.error(request, f'Error loading iron status: {str(e)}')
        return redirect('donor_login')


# bloodbank/blood/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DonorProfile, DonorIronStatus

def add_donor_iron_status(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('donor_name')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            hemoglobin = request.POST.get('hemoglobin')
            ferritin = request.POST.get('ferritin')
            transferrin_sat = request.POST.get('transferrin_sat')
            tibc = request.POST.get('tibc')
            donations = request.POST.get('donations')

            # Validate required fields
            if not all([name, gender, age, hemoglobin, ferritin, transferrin_sat, tibc, donations]):
                messages.error(request, 'All fields are required.')
                return render(request, 'add_donor_iron.html')

            # Convert to appropriate types
            age = int(age) if age else 0  # Default to 0 if None
            hemoglobin = float(hemoglobin) if hemoglobin else 0.0  # Default to 0.0 if None
            ferritin = float(ferritin) if ferritin else 0.0  # Default to 0.0 if None
            transferrin_sat = float(transferrin_sat) if transferrin_sat else 0.0  # Default to 0.0 if None
            tibc = float(tibc) if tibc else 0.0  # Default to 0.0 if None
            donations = int(donations) if donations else 0  # Default to 0 if None

            # Create or update donor profile
            donor, created = DonorProfile.objects.get_or_create(
                donor_name=name,
                defaults={'gender': gender, 'age': age}
            )

            # Create or update iron status
            DonorIronStatus.objects.update_or_create(
                donor=donor,
                defaults={
                    'hemoglobin_level': hemoglobin,
                    'serum_ferritin': ferritin,
                    'transferrin_saturation_index': transferrin_sat,
                    'total_iron_binding_capacity': tibc,
                    'donation_count_last_year': donations,
                }
            )

            messages.success(request, 'Iron status and diet plan updated successfully!')
            return redirect('donor_iron_status_list')  # Ensure this matches your URL pattern

        except ValueError as ve:
            messages.error(request, f'Invalid input: {str(ve)}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'add_donor_iron.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BloodRecipient, BloodType
import re

def recipient_register(request):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            blood_type = request.POST.get('blood_type', '')
            age = request.POST.get('age', '')
            gender = request.POST.get('gender', '')
            contact = request.POST.get('contact', '')
            email = request.POST.get('email', '').strip()
            address = request.POST.get('address', '').strip()
            medical_history = request.POST.get('medical_history', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            # Debug print
            print(f"Received blood type: {blood_type}")
            
            # Get blood type instance
            try:
                blood_type_instance = BloodType.objects.get(blood_group=blood_type)
            except BloodType.DoesNotExist:
                print(f"Blood type not found: {blood_type}")
                messages.error(request, f'Invalid blood type: {blood_type}')
                return redirect('recipient_register')

            # Convert age to integer
            try:
                age_int = int(age)
            except ValueError:
                messages.error(request, 'Invalid age format')
                return redirect('recipient_register')

            # Create recipient
            try:
                recipient = BloodRecipient(
                    recipient_name=name,
                    blood_type=blood_type_instance,
                    age=age_int,
                    gender=gender,
                    contact_number=contact,
                    email=email,
                    address=address,
                    medical_history=medical_history,
                    password=make_password(password)
                )
                recipient.save()
                print("Recipient created successfully")
                
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
                
            except Exception as e:
                print(f"Error creating recipient: {str(e)}")
                messages.error(request, f'Error creating recipient: {str(e)}')
                return redirect('recipient_register')

        except Exception as e:
            print(f"Outer exception: {str(e)}")
            messages.error(request, f'Registration error: {str(e)}')
            return redirect('recipient_register')

    return render(request, 'recipient_register.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import BloodRecipient, BloodRequest  # Import your models
from django.db.models import Q
from datetime import datetime

def recipient_dashboard(request):
    # Check if user is logged in
    recipient_id = request.session.get('recipient_id')
    if not recipient_id:
        messages.error(request, 'Please login to access dashboard')
        return redirect('login')

    try:
        # Get recipient details
        recipient = BloodRecipient.objects.get(recipient_id=recipient_id)
        
        # Get recipient's blood requests using requester_name
        blood_requests = BloodRequest.objects.filter(
            requester_name=recipient.recipient_name
        ).order_by('-request_date')

        context = {
            'recipient': recipient,
            'blood_requests': blood_requests,
        }
        return render(request, 'recipient_dashboard.html', context)

    except BloodRecipient.DoesNotExist:
        messages.error(request, 'Recipient not found')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')

def update_recipient_profile(request):
    if not request.session.get('recipient_id'):
        return redirect('login')
    
    try:
        recipient = BloodRecipient.objects.get(recipient_id=request.session['recipient_id'])
        
        if request.method == 'POST':
            recipient.recipient_name = request.POST.get('name')
            recipient.contact_number = request.POST.get('contact')
            recipient.address = request.POST.get('address')
            recipient.medical_history = request.POST.get('medical_history')
            recipient.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('recipient_dashboard')
            
        return redirect('recipient_dashboard')
        
    except BloodRecipient.DoesNotExist:
        messages.error(request, 'Recipient not found')
        return redirect('login')
    
from django.shortcuts import render, get_object_or_404
from .models import DonorProfile, BloodTest, BloodDonationRequest
from .ml_model import IronPredictionModel
from datetime import datetime

def predict_iron_diet(request, donor_id):
    try:
        # Get donor profile
        donor = get_object_or_404(DonorProfile, donor_id=donor_id)
        
        # Get latest blood test
        latest_blood_test = BloodTest.objects.filter(
            donation__donor=donor
        ).order_by('-test_date').first()
        
        if not latest_blood_test:
            return render(request, 'error.html', {
                'error': 'No blood test found',
                'error_details': 'Please complete a blood test first.'
            })
        
        # Initialize AI model
        model = IronPredictionModel()
        
        # Get prediction
        prediction = model.predict_iron_status(latest_blood_test.hemoglobin)
        
        # Get recommendations based on severity
        recommendations = get_diet_recommendations(prediction['severity'])
        
        context = {
            'donor': donor,
            'blood_test': latest_blood_test,
            'hemoglobin': float(latest_blood_test.hemoglobin),
            'severity': prediction['severity'],
            'confidence': prediction['confidence'],
            'diet_recommendations': recommendations['diet'],
            'supplements': recommendations['supplements'],
            'lifestyle_tips': recommendations['lifestyle_tips'],
            'meal_plan': recommendations['meal_plan'],
            'test_date': latest_blood_test.test_date,
            'prediction_date': datetime.now()
        }
        
        return render(request, 'iron_diet_recommendation.html', context)
        
    except Exception as e:
        print(f"Error in view: {e}")
        return render(request, 'error.html', {
            'error': 'An error occurred',
            'error_details': str(e)
        })
from django.shortcuts import render, get_object_or_404
from .models import DonorProfile, BloodTest
from .ml_model import IronPredictionModel
from datetime import datetime

def get_diet_recommendations(severity):
    """Get diet and supplement recommendations based on severity level"""
    recommendations = {
        'severe': {
            'diet': [
                'Iron-fortified cereals',
                'Spinach and leafy greens',
                'Legumes and lentils',
                'Red meat (if non-vegetarian)',
                'Vitamin C rich fruits'
            ],
            'supplements': {
                'Iron': '100-200mg daily',
                'Vitamin C': '500mg daily',
                'Vitamin B12': '1000mcg daily'
            },
            'meal_plan': {
                'Breakfast': 'Iron-fortified cereal with vitamin C rich fruit',
                'Lunch': 'Spinach salad with citrus dressing',
                'Dinner': 'Lentil soup with dark leafy greens',
                'Snacks': 'Dried fruits and nuts'
            },
            'lifestyle_tips': [
                'Take iron supplements on empty stomach',
                'Avoid tea/coffee with meals',
                'Include vitamin C rich foods with meals',
                'Regular exercise but avoid overexertion',
                'Get adequate rest'
            ]
        },
        'moderate': {
            'diet': [
                'Whole grain breads',
                'Green vegetables',
                'Beans and pulses',
                'Fish (if non-vegetarian)',
                'Citrus fruits'
            ],
            'supplements': {
                'Iron': '50-100mg daily',
                'Vitamin C': '250mg daily',
                'Vitamin B12': '500mcg daily'
            },
            'meal_plan': {
                'Breakfast': 'Whole grain toast with eggs',
                'Lunch': 'Bean soup with vegetables',
                'Dinner': 'Fish/tofu with green vegetables',
                'Snacks': 'Fresh fruits and nuts'
            },
            'lifestyle_tips': [
                'Regular iron-rich meals',
                'Moderate exercise',
                'Good sleep schedule',
                'Stay hydrated',
                'Monitor iron levels'
            ]
        },
        'mild': {
            'diet': [
                'Iron-enriched foods',
                'Dark green vegetables',
                'Nuts and seeds',
                'Lean meats',
                'Dried fruits'
            ],
            'supplements': {
                'Iron': '25-50mg daily',
                'Vitamin C': '100mg daily',
                'Multivitamin': 'As directed'
            },
            'meal_plan': {
                'Breakfast': 'Oatmeal with nuts and fruits',
                'Lunch': 'Mixed vegetable salad',
                'Dinner': 'Lean protein with vegetables',
                'Snacks': 'Trail mix'
            },
            'lifestyle_tips': [
                'Balanced diet',
                'Regular exercise',
                'Adequate hydration',
                'Regular check-ups',
                'Healthy lifestyle'
            ]
        },
        'normal': {
            'diet': [
                'Balanced diet',
                'Variety of vegetables',
                'Whole grains',
                'Lean proteins',
                'Fresh fruits'
            ],
            'supplements': {
                'Multivitamin': 'As directed',
                'Iron': 'Not required unless prescribed',
                'Vitamin C': 'From natural sources'
            },
            'meal_plan': {
                'Breakfast': 'Balanced breakfast with fruits',
                'Lunch': 'Mixed vegetables and protein',
                'Dinner': 'Light and nutritious meal',
                'Snacks': 'Healthy snacks'
            },
            'lifestyle_tips': [
                'Maintain healthy diet',
                'Regular exercise',
                'Good sleep habits',
                'Stay hydrated',
                'Regular check-ups'
            ]
        }
    }
    
    return recommendations.get(severity, recommendations['normal'])

def predict_iron_diet(request, donor_id):
    try:
        # Get donor profile
        donor = get_object_or_404(DonorProfile, donor_id=donor_id)
        
        # Get latest blood test
        latest_blood_test = BloodTest.objects.filter(
            donation__donor=donor
        ).order_by('-test_date').first()
        
        if not latest_blood_test:
            return render(request, 'error.html', {
                'error': 'No blood test found',
                'error_details': 'Please complete a blood test first.'
            })
        
        # Initialize AI model
        model = IronPredictionModel()
        
        # Get prediction
        prediction = model.predict_iron_status(latest_blood_test.hemoglobin)
        
        # Get recommendations based on severity
        recommendations = get_diet_recommendations(prediction['severity'])
        
        context = {
            'donor': donor,
            'blood_test': latest_blood_test,
            'hemoglobin': float(latest_blood_test.hemoglobin),
            'severity': prediction['severity'],
            'confidence': prediction['confidence'],
            'diet_recommendations': recommendations['diet'],
            'supplements': recommendations['supplements'],
            'lifestyle_tips': recommendations['lifestyle_tips'],
            'meal_plan': recommendations['meal_plan'],
            'test_date': latest_blood_test.test_date,
            'prediction_date': datetime.now()
        }
        
        return render(request, 'iron_diet_recommendation.html', context)
        
    except Exception as e:
        print(f"Error in view: {e}")
        return render(request, 'error.html', {
            'error': 'An error occurred',
            'error_details': str(e)
        })


from django.contrib.auth.hashers import make_password
from .models import Admin

def admin_register(request):
    # Only allow access if an admin is already logged in
    if not request.session.get('admin_email'):
        messages.error(request, "Only existing administrators can register new admins.")
        return redirect('admin_login')

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            # Validation
            if Admin.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('admin_register')

            if Admin.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('admin_register')

            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('admin_register')

            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return redirect('admin_register')

            # Create new admin
            new_admin = Admin(
                username=username,
                email=email,
                password=make_password(password),  # Hash the password
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            new_admin.save()

            messages.success(request, 'New administrator registered successfully!')
            return redirect('blood_admin')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('admin_register')

    return render(request, 'admin_register.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BloodType, Admin

def add_blood_type(request):
    try:
        # Get all blood types for display
        blood_types = BloodType.objects.all().order_by('blood_group')
        
        if request.method == 'POST':
            blood_group = request.POST.get('blood_group').upper()  # Convert to uppercase
            
            # Validation
            if not blood_group:
                messages.error(request, 'Blood group is required.')
                return redirect('add_blood_type')
                
            # Check if blood group already exists
            if BloodType.objects.filter(blood_group=blood_group).exists():
                messages.error(request, f'Blood group {blood_group} already exists.')
                return redirect('add_blood_type')
                
            try:
                # Create new blood type
                blood_type = BloodType.objects.create(blood_group=blood_group)
                messages.success(request, f'Blood group {blood_group} added successfully!')
                return redirect('add_blood_type')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('add_blood_type')

        return render(request, 'add_blood_type.html', {
            'blood_types': blood_types,
            'admin_email': request.session.get('admin_email', None)
        })
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('blood_admin')