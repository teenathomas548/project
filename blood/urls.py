from django.urls import path
from.import views
from django.contrib.auth import views as auth_views


urlpatterns = [
     path('',views.home, name = 'home'),
     path('register/',views.register,name ='register'),
     path('login/',views.login,name='login'),
     path('blood_admin/', views.blood_admin, name='blood_admin'),
     path('admin_login/',views.admin_login,name='admin_login'),
     path('userhome/', views.userhome, name='userhome'),
     path('about/', views.about, name='about'),
     path('userrhome', views.userrhome, name='userrhome'),

]

