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
from .models import BloodDonor
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
        #elif role == 'donate':
            # BloodDonor.objects.create(user=registration, blood_type=blood_group)

        return redirect('login')
    else:
        return render(request, 'register.html')


    

def userhome(request):
    """
    Render the user home page.
    """
    return render(request, 'userhome.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Use Django ORM to authenticate the user
            try:
                user = Registration.objects.get(email=email, password=password)
                
                # Check if the user is active
                if not user.is_active:
                    messages.error(request, 'Your account is inactive. Please contact support.')
                    return render(request, 'login.html', {'form': form})
                
                role = user.role  # Assuming the role is stored in the `role` field

                # Set user in session
                request.session['email'] = email
                request.session['role'] = role

                # Redirect based on role
                if role == 'donate':
                    return redirect('donor_dashboard')  # Redirect to donor dashboard
                elif role == 'recipient':
                    return redirect('recipient_home')  # Redirect to recipient dashboard
                else:
                    messages.error(request, 'Invalid user role')

            except Registration.DoesNotExist:
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

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

from django.shortcuts import render
from django.db.models import Sum
from .models import Registration, Inventory, BloodRequest

def blood_admin(request):
    # Total donors count
    total_donors = Registration.objects.filter(role='donate').count()

    # Total available blood units
    blood_units = Inventory.objects.aggregate(total_units=Sum('units_available'))['total_units'] or 0

    # Pending requests count
    pending_requests = BloodRequest.objects.filter(status='pending').count()
    
    # Urgent requests count
    urgent_requests = BloodRequest.objects.filter(status='urgent').count()

    # Completed requests count
    completed_requests = BloodRequest.objects.filter(status='approved').count()

    # Fetch recent activities dynamically
    recent_activities = [
        {
            "date": request.request_date,
            "activity": f"{request.requester_name} requested blood of group {request.blood_group} from {request.hospital_name}",
            "status": request.status  # this will show 'pending', 'urgent', or 'approved'
        }
        for request in BloodRequest.objects.order_by('-request_date')[:5]  # limit to 5 recent requests
    ]

    context = {
        "total_donors": total_donors,
        "blood_units": blood_units,
        "pending_requests": pending_requests,
        "urgent_requests": urgent_requests,
        "completed_requests": completed_requests,
        "recent_activities": recent_activities,
    }

    return render(request, 'blood_admin.html', context)


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




def donor_dashboard(request):
    # Assume donor and their data are fetched from the database
    donor = request.user  # or however you fetch the donor
    donation_history = []  # Fetch from database
    upcoming_appointments = []  # Fetch from database
    eligibility_status = "Eligible for donation"  # Logic to determine eligibility

    context = {
        'donor': donor,
        'donation_history': donation_history,
        'upcoming_appointments': upcoming_appointments,
        'eligibility_status': eligibility_status,
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


def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            form.save()  # Save the valid form data to the database
            return redirect('success')  # Redirect after successful submission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BloodRequestForm()
    
    return render(request, 'request_blood.html', {'form': form})


def success_view(request):
    return render(request, 'success.html')


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




def donor_profile(request):
    email = request.session.get('email')

    if email:
        try:
            registration = Registration.objects.get(email=email, role='donate')
            error = None
        except Registration.DoesNotExist:
            registration = None
            error = 'Profile not found for donor'
    else:
        registration = None
        error = 'Email not found in session'

    return render(request, 'donor_profile.html', {
        'registration': registration,
        'error': error
    })




from .forms import DonorEditForm


def donor_edit_profile(request):
    email = request.session.get('email')  # Get email from session

    if email:
        # Fetch the donor's registration based on the email and role
        registration = get_object_or_404(Registration, email=email, role='donate')  # Use the correct role
        
    else:
        messages.error(request, 'Email not found in session')
        return redirect('donor_dashboard')  # Redirect if email not found

    if request.method == 'POST':
        form = DonorEditForm(request.POST, instance=registration)  # Bind form with existing data
        if form.is_valid():
            form.save()  # Save the updated registration data
            messages.success(request, 'Profile updated successfully!')
            return redirect('donor_dashboard')  # Redirect to the profile view after saving
    else:
        form = DonorEditForm(instance=registration)  # Pre-fill form with existing data

    return render(request, 'donor_edit_profile.html', {
        'form': form,
    })


