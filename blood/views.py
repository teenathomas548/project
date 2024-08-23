from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.db import IntegrityError
from .forms import LoginForm
from django.shortcuts import render, redirect
from .models import Registration
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm




def register(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        username = request.POST['username']
        password = request.POST['password']
        phone_number = request.POST['phone_number']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date_of_birth = request.POST['dob']
        role = request.POST['role']
  
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO `registrations`
                    (`first_name`, `last_name`, `date_of_birth`, `username`, `password`, `phone_number`, `gender`, `blood_group`, `role`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [first_name, last_name,date_of_birth, username, password, phone_number, gender, blood_group, role])
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
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Use raw SQL to authenticate the user
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', [username, password])
                user = cursor.fetchone()

            if user:
                # Set user in session or perform other login actions
                request.session['username'] = username
                return redirect('userhome')  # Redirect to a page after successful login
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


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

def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Use raw SQL to authenticate the user
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', [username, password])
                user = cursor.fetchone()

            if user:
                # Set user in session or perform other login actions
                request.session['username'] = username
                return redirect('blood_admin')  # Redirect to a page after successful login
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'home.html') 


class PasswordResetRequestView(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'