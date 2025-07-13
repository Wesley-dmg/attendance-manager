from django.contrib import messages
from django.shortcuts import render, redirect

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import *


def is_admin(user):
    return user.is_admin


def AdminDashboardView(request):

    context = {}
    return render(request, "home/admin_dashboard.html", context)


def TeacherDashboardView(request):

    context = {}
    return render(request, "home/teacher_dashboard.html", context)


def index(request):

    context = {
        "segment": "index",
    }
    return render(request, "pages/index.html", context)


def tables(request):
    context = {"segment": "tables"}
    return render(request, "pages/dynamic-tables.html", context)


def ma_vue(request):
    from django.contrib.auth import get_user_model

    User = get_user_model()  # Récupère le modèle d'utilisateur

    # Remplace 'mon_username' par le nom d'utilisateur que tu veux tester
    try:
        user = User.objects.get(username="wesleydmg")
    except User.DoesNotExist:
        print("L'utilisateur n'existe pas.")
    # Vérifier si l'utilisateur a la permission
    has_permission = request.user.has_perm("users.view_parentprofile")

    # Vérifie si l'utilisateur a la permission 'apps.users.view_parentprofil'
    if user.is_authenticated:
        print(
            "L'utilisateur est connecté "
            + user.first_name
            + " "
            + user.last_name
            + " "
            + user.username
        )
        if user.has_perm("users.view_parentprofile"):
            print("La permission est bien assignée.")
        else:
            print("La permission n'est pas assignée ou le nom est incorrect.")
    return render(request, "home/test.html")
