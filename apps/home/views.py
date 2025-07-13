# from django.contrib import messages
from django.shortcuts import render, redirect

# from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import *


def is_admin(user):
    return user.is_admin

@login_required
def index(request):

    context = {
        "segment": "index",
    }
    return render(request, "home/index.html", context)

@login_required
def admin(request):

    context = {
        "segment": "index",
    }
    return render(request, "home/dashboard.html", context)


def tables(request):
    context = {"segment": "tables"}
    return render(request, "pages/dynamic-tables.html", context)
