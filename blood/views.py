from pyexpat.errors import messages
from urllib.request import Request
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.db import connection
from django.db import IntegrityError
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from .forms import RegistrationForm
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Registration
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Campaign
from .forms import CampaignForm
from django.utils import timezone
from .models import Inventory,BloodType
from .forms import InventoryForm
from django.core.exceptions import ValidationError
from django.db import connection, IntegrityError
from .models import BloodDonor
from .models import Recipient
from django.db.models import Count, Sum  # Import Sum here
from datetime import date
from .forms import BloodRequestForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Registration
from .models import Admin  # Assuming you have a BloodAdmin model


# About page view
def about(request):
    return render(request, 'about.html')



def register(request):
    if request.method == 'POST':
        # Retrieving form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        gender = request.POST.get('gender')
        blood_group_str = request.POST.get('blood_group')  # This should be the blood group string (e.g., 'AB+')
        date_of_birth = request.POST.get('date_of_birth')
        role = request.POST.get('role')  # Make sure 'role' is correctly set

        # Validate that no fields are empty (simple validation)
        if not all([first_name, last_name, email, password, phone_number, gender, blood_group_str, date_of_birth, role]):
            error_message = "Please fill in all the fields."
            return render(request, 'register.html', {'error_message': error_message})

        try:
            # Get the blood type object based on the blood group string
            blood_group = get_object_or_404(BloodType, blood_group=blood_group_str)

            # Create the registration instance, with the password hashed
            registration = Registration.objects.create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                email=email,
                password=password,  # Hashing the password for security
                phone_number=phone_number,
                gender=gender,
                blood_group=blood_group,  # Use the BloodType object directly
                role=role
            )

            # If the role is 'donate', insert into 'blood_donors' table
            if role == 'donate':
                BloodDonor.objects.create(
                    user=registration,
                    blood_type=blood_group,
                    last_donation_date=None  # You can set this to a specific date if applicable
                )

            # If the role is 'recipient', insert into 'recipient' table
            elif role == 'recipient':
                Recipient.objects.create(
                    user=registration,
                    blood_type=blood_group
                )

            # Redirect to login page or success page after registration
            return redirect('login')

        except IntegrityError:
            error_message = "A user with this email already exists."
            return render(request, 'register.html', {'error_message': error_message})

    # For GET requests, render the registration page
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

            # Use Django ORM to authenticate the user
            try:
                admin_user = Admin.objects.get(email=email, password=password)

                # Set user in session
                request.session['email'] = email
                return redirect('blood_admin')  # Redirect to a page after successful login

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

def blood_admin(request):
    # Total donors count - assuming 'Registration' model corresponds to the 'registrations' table
    total_donors = Registration.objects.filter(role='donate').count()

    # Total available blood units - assuming 'Inventory' model corresponds to 'blood_inventory' table
    blood_units = Inventory.objects.aggregate(total_units=Sum('units_available'))['total_units'] or 0

    # Pending requests count - assuming you have a 'Request' model (if not, remove this line)

    # Example recent activities
    recent_activities = [
        {"date": "2024-08-16", "activity": "Donor John Doe scheduled an appointment", "status": "Completed"},
        {"date": "2024-08-15", "activity": "Blood donation campaign created", "status": "Pending"},
        {"date": "2024-08-14", "activity": "Recipient Jane Doe requested blood", "status": "Urgent"},
    ]

    context = {
        "total_donors": total_donors,
        "blood_units": blood_units,
        "recent_activities": recent_activities,
    }

    return render(request, 'blood_admin.html', context)


def disable_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.first_name} {user.last_name} has been disabled.')
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
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect('campaign_list')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'campaign_form.html', {'form': form, 'action': 'Edit'})

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
    # Assuming you have a `registrations` table and filtering users with the role of 'recipient'
    recipient = request.user  # The logged-in recipient
    
    # Pass recipient data to the template
    context = {
        'recipient': recipient,
        # Add more context if needed, like recipient requests or notifications
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
            form.save()  # Save the blood request to the database
            return redirect('success')  # Redirect to a success page or wherever you want
    else:
        form = BloodRequestForm()
    
    return render(request, 'request_blood.html', {'form': form})

def success_view(request):
    return render(request, 'success.html')


# def recipient_profile(request):
#     try:
#         # Get the Registration object related to the logged-in user using user_id
#         registration = Registration.objects.get(user_id=request.user.id)
#     except Registration.DoesNotExist:
#         registration = None  # Handle the case where the registration is not found

#     return render(request, 'recipient_profile1.html', {
#         'registration': registration,
#         'error': 'Profile not found' if registration is None else None
#     })      


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
