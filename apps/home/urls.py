from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'home'  # Namespace for this application

urlpatterns = [
  path('Administration/', views.AdminDashboardView, name='admin_dashboard'),

  path(''       , views.index,  name='index'),
  path('tables/', views.tables, name='tables'),
  
  
]
