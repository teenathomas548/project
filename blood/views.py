from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.db import IntegrityError
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from .forms import RegistrationForm




from django.shortcuts import render

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
                cursor.execute('SELECT * FROM registrations WHERE email = %s AND password = %s', [email, password])
                user = cursor.fetchone()

            if user:
                # Set user in session or perform other login actions
                request.session['email'] = email
                return redirect('userrhome')  # Redirect to a page after successful login
            else:
                messages.error(request, 'Invalid username or password')
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
