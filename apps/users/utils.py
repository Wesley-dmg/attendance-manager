import uuid
import hashlib
from django.views.decorators.http import require_GET
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

from django.utils.dateformat import format as date_format

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


# class UserSearchView(LoginRequiredMixin, AdminTestMixin, View):
#     def get(self, request):
#         query = request.GET.get("q", "")
#         role = request.GET.get("role", "")

#         users = CustomUser.objects.filter(
#             Q(first_name__icontains=query)
#             | Q(last_name__icontains=query)
#             | Q(phone_number__icontains=query)
#         )

#         if role:
#             users = users.filter(role=role)

#         html = render_to_string(
#             "users/partials/_user_cards.html", {"users": users}, request=request
#         )
#         return JsonResponse({"html": html})


class UserSearchView(LoginRequiredMixin, AdminTestMixin, View):
    """
    Retourne le partial HTML des cartes utilisateurs filtrées (search ajax).
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        role = request.GET.get("role", "").strip()

        users = User.objects.all().order_by("first_name", "last_name")

        if query:
            users = users.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(email__icontains=query)
            )

        if role:
            users = users.filter(role=role)

        # mapping role -> noms d'url utilisées dans le partial
        role_map = {
            "admin": {
                "detail_url": "users:admin_detail",
                "edit_url": "users:edit_admin",
                "delete_url": "users:delete_admin",
            },
            "teacher": {
                "detail_url": "users:teacher_detail",
                "edit_url": "users:edit_teacher",
                "delete_url": "users:delete_teacher",
            },
            "student": {
                "detail_url": "users:student_detail",
                "edit_url": "users:edit_student",
                "delete_url": "users:delete_student",
            },
            "parent": {
                "detail_url": "users:parent_detail",
                "edit_url": "users:edit_parent",
                "delete_url": "users:delete_parent",
            },
        }

        # si role absent ou inconnu, on prend un fallback (ajuste si tes noms d'urls diffèrent)
        urls = role_map.get(
            role,
            {
                "detail_url": "users:student_detail",
                "edit_url": "users:edit_student",
                "delete_url": "users:delete_student",
            },
        )

        context = {"users": users, **urls}

        html = render_to_string(
            "users/partials/_user_cards.html", context, request=request
        )
        return JsonResponse({"html": html})


@require_GET
def check_parent_phone(request):
    phone = request.GET.get("phone")
    if not phone:
        return JsonResponse({"exists": False})

    try:
        user = User.objects.get(phone_number=phone, role="parent")
        parent_profile = user.parentprofile
        return JsonResponse(
            {
                "exists": True,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email or "",
                "date_of_birth": (
                    date_format(user.date_of_birth, "Y-m-d")
                    if user.date_of_birth
                    else ""
                ),
                "gender": user.gender or "",
                "relation": parent_profile.relation or "guardian",
            }
        )
    except User.DoesNotExist:
        return JsonResponse({"exists": False})


class FilterByFiliereView(LoginRequiredMixin, AdminTestMixin, View):
    def get(self, request):
        filiere_id = request.GET.get("filiere", "")

        # On prend uniquement les étudiants
        qs = CustomUser.objects.filter(role="student")

        if filiere_id:
            qs = qs.filter(studentprofile__major_id=filiere_id)

        # On définit les noms de vues pour le partial
        urls = {
            "detail_url": "users:student_detail",
            "edit_url": "users:edit_student",
            "delete_url": "users:delete_student",
        }

        html = render_to_string(
            "users/partials/_user_cards.html", {"users": qs, **urls}, request=request
        )
        return JsonResponse({"html": html})
