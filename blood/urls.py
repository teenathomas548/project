from django.urls import path, include
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
from .views import donor_login  # If using function-based view
from .views import book_appointment
from .views import  submission_success  # Update the im
from .views import apply_blood  # Make sure this import is present
from .views import  approve_request
from .views import manage_donors, disable_donor, enable_donor
from .views import manage_doctors, disable_doctor, enable_doctor
from .views import blood_admin, all_pending_requests
from .views import register_admin
from .views import give_feedback, feedback_success
#from .views import manage_feedback, download_feedback_pdf
from .views import hospital_report

from .views import emergency_alert_page
from .views import manage_appointments
from .views import download_hospital_report_pdf
from .views import manage_feedback
from .views import custom_login_view
from .views import blood_camp_locator 
from .views import find_available_donors # Import your views
from .views import donor_iron_status_list, add_donor_iron_status


urlpatterns = [
     path('',views.home, name = 'home'),
     path('register/',views.register,name ='register'),
    path('login/', custom_login_view, name='login'),
    path('blood_admin/', views.blood_admin, name='blood_admin'),
    path('all-pending-requests/', all_pending_requests, name='all_pending_requests'),
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
    # path('recipient/profile/', recipient_profile, name='recipient_profile'),
    # path('recipient/edit-profile/', recipient_edit_profile, name='recipient_edit_profile'),
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
    path('register-donor/', views.register_donor, name='register_donor'),
    path('donor/login/', views.donor_login, name='donor_login'),  # Donor login URL

    path('donor/book-appointment/', views.book_appointment, name='book_appointment'),
    path('donor/', views.first_time_donation, name='first_time_donation'),
    path('submit-medical-records/', views.submit_medical_records, name='submit_medical_records'),
    path('submission-success/', submission_success, name='submission_success'),  # Add this line
    path('apply_blood/', apply_blood, name='apply_blood'),  # URL for applying for blood
    path('approve_request/<int:request_id>/', approve_request, name='approve_request'),  # New URL pattern for approval
    path('manage-donors/', manage_donors, name='manage_donors'),
    path('disable-donor/<int:donor_id>/', disable_donor, name='disable_donor'),
    path('enable-donor/<int:donor_id>/', enable_donor, name='enable_donor'),
    path('manage-doctors/', manage_doctors, name='manage_doctors'),
    path('disable-doctor/<int:doctor_id>/', disable_doctor, name='disable_doctor'),
    path('enable-doctor/<int:doctor_id>/', enable_doctor, name='enable_doctor'),
    path('pending-hospitals/', views.pending_hospitals, name='pending_hospitals'),
    path('approve-hospital/<int:hospital_id>/', views.approve_hospital, name='approve_hospital'),    
    path('oauth/', include('social_django.urls', namespace='social')),
    path('register/admin/', register_admin, name='admin_register'),  # Custom URL for Admin Registration


    #path('platelets-donation/', views.platelets_donation_request, name='platelets_donation_request'),
   # path('donation-status/', views.platelets_donation_status, name='platelets_donation_status'),
    path('plasma-donation/', views.plasma_donation_request, name='plasma_donation_request'),
    path('plasma-donation/sucess/', views.plasma_sucess, name='plasma_sucess'),

    path('plasma-requests/', views.plasma_requests_page, name='plasma_requests_page'),
    path('approve-plasma-request/<int:request_id>/', views.approve_plasma_request, name='approve_plasma_request'),
    path('reject-plasma-request/<int:request_id>/', views.reject_plasma_request, name='reject_plasma_request'),
    path('plasma-request/success/', views.plasma_application_success, name='plasma_application_success'),
    path('plasma-request/', views.plasma_request_view, name='plasma_request'),
    path('donor/feedback/', give_feedback, name='give_feedback'),
    path('donor/feedback/success/', feedback_success, name='feedback_success'),
    path('feedback/manage/', manage_feedback, name='manage_feedback'),
    #('feedback/download/', download_feedback_pdf, name='download_feedback_pdf'),
    path('emergency-alert/', emergency_alert_page, name='emergency_alert'),
    path("manage-appointments/", manage_appointments, name="manage_appointments"),
    path('reports/hospital/<int:hospital_id>/', views.hospital_report, name='hospital_report'),
    path('download-hospital-report/', download_hospital_report_pdf, name='download_hospital_report_pdf'),
    path('manage-feedback/', manage_feedback, name='manage_feedback'),

    # Blood Donation Process URLs
    path('request-donation/', views.request_blood_donation, name='request_donation'),
    path('donation-steps/', views.donation_steps, name='donation_steps'),
    path('donation-history/', views.donor_donation_history, name='donation_history'),
    
    # Optional: Additional URLs for managing donations
    path('cancel-donation/<int:request_id>/', views.cancel_donation, name='cancel_donation'),
    path('reschedule-donation/<int:request_id>/', views.reschedule_donation, name='reschedule_donation'),
    path('basic-screening/<int:request_id>/', views.basic_screening, name='basic_screening'),
     path('manage-donation-requests/', views.manage_donation_requests, name='manage_donation_requests'),
    path('update-donation-status/<int:request_id>/', views.update_donation_status, name='update_donation_status'),
    path('test/apply/<int:donation_id>/', views.apply_test, name='apply_test'),
    path('test/view/<int:test_id>/', views.view_test, name='view_test'),
    path('test/list/', views.test_list, name='test_list'),
    path('test/pending/', views.pending_test, name='pending_test'),
    path('test/print/<int:test_id>/', views.print_test, name='print_test'),
    path('change-password/', views.change_password, name='change_password'),
    path('admin_test_list/', views.admin_test_list, name='admin_test_list'),
    path('print_test/<int:test_id>/', views.print_test, name='print_test'),
    path('blood-camps/', blood_camp_locator, name='blood_camp_locator'),
    path('matches/find/', views.find_matches, name='find_matches'),
    path('matches/<int:match_id>/', views.match_details, name='match_details'),
    path('predict-demand/', views.predict_demand, name='predict_demand'),
    # path('predict-campaign/', views.predict_campaign_success, name='predict_campaign'),
    path('donor-health-list/', views.donor_health_list, name='donor_health_list'),
    path('health-risk-assessment/<int:donor_id>/', views.assess_donor_health, name='health_risk_assessment'),
    path('health-risk/', views.health_risk_view, name='health_risk'),  # Changed name and path
    path('inter-hospital-request/', views.inter_hospital_request, name='inter_hospital_request'),
    path('hospital-requests/', views.hospital_requests, name='hospital_requests'),
    path('process-request/<int:transfer_id>/', views.process_request, name='process_request'),
    path('donor-card/', views.donor_card, name='donor_card'),
    path('donors/available/<int:blood_request_id>/', find_available_donors, name='find_available_donors'),
     path('donor-iron-status/', donor_iron_status_list, name='donor_iron_status_list'),
    path('add-donor-iron-status/', add_donor_iron_status, name='add_donor_iron_status'),
    path('recipient/register/', views.recipient_register, name='recipient_register'),
path('recipient/dashboard/', views.recipient_dashboard, name='recipient_dashboard'),
    path('recipient/update-profile/', views.update_recipient_profile, name='update_recipient_profile'),
    path('iron-diet/<int:donor_id>/', views.predict_iron_diet, name='predict_iron_diet'),  # With donor_id
    # path('iron-diet/', views.predict_iron_diet_redirect, name='predict_iron_diet_redirect'),  # Without donor_id
    path('show-campaign-success/<int:campaign_id>/', views.show_campaign_success, name='show_campaign_success'),
    path('add-blood-type/', views.add_blood_type, name='add_blood_type'),






    
]

