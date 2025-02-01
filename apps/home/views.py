from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required

from .models import *

def is_admin(user):
    return user.is_admin

@login_required
@user_passes_test(is_admin)
def AdminDashboardView(request):

    context = {
    
    }
    return render(request, "home/admin_dashboard.html", context)

def TeacherDashboardView(request):

    context = {
    
    }
    return render(request, "home/teacher_dashboard.html", context)

def index(request):

  context = {
    'segment'  : 'index',
  }
  return render(request, "pages/index.html", context)

def tables(request):
  context = {
    'segment': 'tables'
  }
  return render(request, "pages/dynamic-tables.html", context)

from django.contrib import messages
from django.shortcuts import render

def ma_vue(request):
    # Ajouter un message de succès
    
    
    # Ajouter un message d'erreur
    messages.error(request, 'Une erreur est survenue.')
    
    # Retourner la réponse avec les messages
    messages.success(request, 'Opération réussie !')
    return render(request, 'home/notification.html')