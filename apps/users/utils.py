import uuid
import hashlib

from django.utils.text import slugify
import random

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.home.mixins import AdminTestMixin
from apps.users.models import CustomUser

User = get_user_model()


def generate_reset_code():
    code = str(uuid.uuid4()).split("-")[0]  # ex: '5f2b1a'
    hashed = hashlib.sha256(code.encode()).hexdigest()
    return code, hashed


def generate_unique_username(base_name: str) -> str:
    base_username = slugify(base_name) or "user"
    username = base_username
    suffix = random.randint(10, 99)

    while User.objects.filter(username=username).exists():
        suffix = random.randint(10, 99)
        username = f"{base_username}{suffix}"

    return username


class UserSearchView(LoginRequiredMixin, AdminTestMixin, View):
    def get(self, request):
        query = request.GET.get("q", "")
        role = request.GET.get("role", "")

        users = CustomUser.objects.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone_number__icontains=query)
        )

        if role:
            users = users.filter(role=role)

        html = render_to_string(
            "users/partials/_user_cards.html", {"users": users}, request=request
        )
        return JsonResponse({"html": html})
