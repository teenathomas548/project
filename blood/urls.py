from django.urls import path
from.import views
from django.contrib.auth import views as auth_views
from .views import donor_dashboard
from .views import manage_campaigns,add_campaign, campaign_edit, disable_campaign,enable_campaign
from .views import recipient_dashboard
from .views import logout_view
from .views import inventory_list, add_inventory, enable_inventory, disable_inventory,edit_inventory
from .views import request_blood
from .views import recipient_profile
from .views import recipient_edit_profile
from .views import donor_profile,donor_edit_profile
from .views import hospital_request_blood
from .views import doctor_register





urlpatterns = [
     path('',views.home, name = 'home'),
     path('register/',views.register,name ='register'),
     path('login/',views.login,name='login'),
     path('blood_admin/', views.blood_admin, name='blood_admin'),
     path('admin_login/',views.admin_login,name='admin_login'),
     path('userhome/', views.userhome, name='userhome'),
     path('about/', views.about, name='about'),
     path('userrhome', views.userrhome, name='userrhome'),
     path('manage_users/', views.manage_users, name='manage_users'),  # Ensure this line exists
     path('disable_user/<int:user_id>/', views.disable_user, name='disable_user'),
     path('enable_user/<int:user_id>/', views.enable_user, name='enable_user'),     
     path('donor/dashboard/', donor_dashboard, name='donor_dashboard'),
     path('campaigns/', views.campaign_list, name='campaign_list'),
     path('manage_campaigns/', manage_campaigns, name='manage_campaigns'),
     path('add_campaign/', add_campaign, name='add_campaign'),
     path('campaign_edit/<int:campaign_id>/', campaign_edit, name='campaign_edit'),
     path('disable_campaign/<int:campaign_id>/', disable_campaign, name='disable_campaign'),
     path('enable_campaign/<int:campaign_id>/', enable_campaign, name='enable_campaign'),
     path('recipient/dashboard/', recipient_dashboard, name='recipient_dashboard'),
     path('logout/', views.logout_view, name='logout'),
     path('latest/', views.latest_campaigns, name='latest_campaigns'),  # Ensure this line exists
     path('logout/', logout_view, name='logout'),
     path('recipient/home/', views.recipient_home, name='recipient_home'),
    path('inventory/', inventory_list, name='inventory_list'),  # URL pattern for the inventory list
    path('inventory/add/', add_inventory, name='add_inventory'),  # URL for adding inventory
    path('inventory/edit/<int:inventory_id>/', edit_inventory, name='edit_inventory'),
    path('inventory/enable/<int:pk>/', enable_inventory, name='enable_inventory'),  # URL to enable inventory
    path('inventory/disable/<int:pk>/', disable_inventory, name='disable_inventory'),
    path('request-blood/', request_blood, name='request_blood'),  # URL for the blood request form
    path('recipient/profile/', recipient_profile, name='recipient_profile'),
    path('recipient/edit-profile/', recipient_edit_profile, name='recipient_edit_profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('donor/profile/', donor_profile, name='donor_profile'),
    path('donor/edit-profile/', views.donor_edit_profile, name='donor_edit_profile'),
    path('search-blood/', views.search_blood, name='search_blood'),
    path('hospital/request-blood/', hospital_request_blood, name='hospital_request_blood'),
    path('payment/', views.payment_page, name='payment'),  # Ensure this is correct
    path('payment-success/', views.payment_success, name='payment_success'),
    path('register-hospital/', views.register_hospital, name='register_hospital'),
    path('hospital_login/', views.hospital_login, name='hospital_login'),
    path('dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('register/doctor/', doctor_register, name='doctor_register'),  # URL for doctor registration
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),  # URL for doctor dashboard
    path('blood-application/success/', views.blood_application_success, name='blood_application_success'),


]