from pyexpat.errors import messages
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

# About page view
def about(request):
    return render(request, 'about.html')



def register(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date_of_birth = request.POST['dob']
        role = request.POST['role']
        email = request.POST['email']
  
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO `registrations`
                    (`first_name`, `last_name`, `date_of_birth`, `email`, `password`, `phone_number`, `gender`, `blood_group`, `role`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [first_name, last_name,date_of_birth, email, password, phone_number, gender, blood_group, role])
            return redirect('login')  # Redirect to a success page
        except IntegrityError:
            error_message = "Username already exists."
            return render(request, 'register.html', {'error_message': error_message})

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

            # Use raw SQL to authenticate the user
            with connection.cursor() as cursor:
                cursor.execute('SELECT role FROM registrations WHERE email = %s AND password = %s', [email, password])
                user = cursor.fetchone()

            if user:
                role = user[0]  # Assuming `role` is stored in the first column of the result
                
                # Set user in session
                request.session['email'] = email
                request.session['role'] = role

                # Redirect based on role
                if role == 'donor':
                    return redirect('donor_dashboard')  # Redirect to donor dashboard
                elif role == 'recipient':
                    return redirect('recipient_dashboard')  # Redirect to recipient dashboard
                else:
                    messages.error(request, 'Invalid user role')

            else:
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

            # Use raw SQL to authenticate the user
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM blood_admin WHERE email = %s AND password = %s', [email, password])
                user = cursor.fetchone()

            if user:
                # Set user in session or perform other login actions
                request.session['email'] = email
                return redirect('blood_admin')  # Redirect to a page after successful login
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'home.html') 

def userrhome(request):
    return render(request, 'userrhome.html')

def blood_admin(request):
    # Example data - replace with your actual model queries
    total_donors = 200  # Replace with your model query
    blood_units_available = 150  # Replace with your model query
    pending_requests = 10  # Replace with your model query
    recent_activities = [
        {"date": "2024-08-16", "activity": "Donor John Doe scheduled an appointment", "status": "Completed"},
        {"date": "2024-08-15", "activity": "Blood donation campaign created", "status": "Pending"},
        {"date": "2024-08-14", "activity": "Recipient Jane Doe requested blood", "status": "Urgent"},
    ]
    
    context = {
        "total_donors": total_donors,
        "blood_units_available": blood_units_available,
        "pending_requests": pending_requests,
        "recent_activities": recent_activities,
    }
    return render(request, 'blood_admin.html', context)

def add_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, 'User added successfully!') 
            return redirect('manage_users')
    else:
        form = RegistrationForm()
    return render(request, 'add_user.html', {'form': form})


def edit_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Update  successfully!')
            return redirect('manage_users')
    else:
        form = RegistrationForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})

def delete_user(request, user_id):
    user = get_object_or_404(Registration, pk=user_id)
    if request.method == 'POST':
        user.delete()  
        messages.success(request, 'Delete a user successfully!')
        return redirect('manage_users')
    return render(request, 'delete_user.html', {'user': user})

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
            form.save()
            return redirect('campaign_list')
    else:
        form = CampaignForm()
    return render(request, 'campaign_form.html', {'form': form, 'action': 'Add'})

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
def campaign_delete(request, campaign_id):
    campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
    if request.method == 'POST':
        campaign.delete()  # Delete the campaign
        return redirect('campaign_list')  # Redirect to a campaign list or any other page after deletion
    return render(request, 'campaign_confirm_delete.html', {'campaign': campaign})

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

