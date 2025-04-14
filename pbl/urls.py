"""
URL configuration for pbl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from myapp.views import date_specific_log
from myapp.views import food_search

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='myapp/home.html'), name='home'),
    path('dashboard/', views.index, name='index'),
    path('delete/<int:id>/', views.delete_consume, name='delete'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('weekly-report/', views.weekly_report, name='weekly_report'),   # New weekly report URL
    path('monthly-report/', views.monthly_report, name='monthly_report'), # New monthly report URL
    path('', date_specific_log, name='index'),
    path('date/<str:selected_date>/', date_specific_log, name='date_log'),
    path('add_custom_food/', views.add_custom_food, name='add_custom_food'),
     path('food-search/', food_search, name='food_search'),
]   


    

