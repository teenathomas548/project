from django.urls import path
from.import views
from django.contrib.auth import views as auth_views
from .views import donor_dashboard
from .views import manage_campaigns,add_campaign, campaign_edit, campaign_delete
from .views import recipient_dashboard



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
     path('add_user/', views.add_user, name='add_user'),
     path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
     path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
     path('donor/dashboard/', donor_dashboard, name='donor_dashboard'),
     path('campaigns/', views.campaign_list, name='campaign_list'),
     path('manage_campaigns/', manage_campaigns, name='manage_campaigns'),
    path('add_campaign/', add_campaign, name='add_campaign'),
    path('campaign_edit/<int:campaign_id>/', campaign_edit, name='campaign_edit'),
    path('campaign_delete/<int:campaign_id>/', campaign_delete, name='campaign_delete'),
    path('recipient/dashboard/', recipient_dashboard, name='recipient_dashboard'),



]