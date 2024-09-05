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
from .forms import PasswordResetRequestForm, SetPasswordForm
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text







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


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetRequestForm(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Lifeline Blood Bank',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    except Exception as e:
                        return render(request, "password_reset_error.html", {"error": str(e)})
                return redirect(reverse('password_reset_done'))
    else:
        password_reset_form = PasswordResetRequestForm()
    return render(request, "password_reset.html", {"password_reset_form": password_reset_form})

def password_reset_done(request):
    return render(request, "password_reset_done.html")

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect(reverse('password_reset_complete'))
        else:
            form = SetPasswordForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        return render(request, 'password_reset_invalid.html')

def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

def about(request):
    return render(request, 'about.html')


def userrhome(request):
    return render(request, 'userrhome.html')