import os
import re
import uuid
import hashlib
from django.conf import settings
from django.contrib.staticfiles import finders
from django.views.decorators.http import require_GET
from django.utils.text import slugify
import random

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.attendance.utils import get_absence_count
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


class UserSearchView(LoginRequiredMixin, AdminTestMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        role = request.GET.get("role", "").strip()
        filiere_id = request.GET.get("filiere", "").strip()

        users = CustomUser.objects.all().order_by("first_name", "last_name")

        if role:
            users = users.filter(role=role)

        if query:
            users = users.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(email__icontains=query)
            )

        if filiere_id:
            users = users.filter(studentprofile__major_id=filiere_id)

        # enrichir absences si on est sur des étudiants
        if role == "student":
            users = users.select_related("studentprofile", "studentprofile__major")
            for student in users:
                if hasattr(student, "studentprofile"):
                    student.absence_count = get_absence_count(student.studentprofile)

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

        urls = role_map.get(
            role,
            {  # fallback = student
                "detail_url": "users:student_detail",
                "edit_url": "users:edit_student",
                "delete_url": "users:delete_student",
            },
        )

        context = {"users": users, "role": role, **urls}

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


def normalize_bj_phone(phone: str) -> str:
    """Normalise en +229XXXXXXXX (8 chiffres). Accepte 'XXXXXXXX', '+229XXXXXXXX', ou '229XXXXXXXX'."""
    phone = (phone or "").replace(" ", "")
    if phone.startswith("+229") and re.fullmatch(r"\+229\d{8}", phone):
        return phone
    if re.fullmatch(r"\d{8}", phone):
        return f"+229{phone}"
    if phone.startswith("229") and re.fullmatch(r"229\d{8}", phone):
        return f"+{phone}"
    # Laisse passer, le model.clean() lèvera une erreur si invalide
    return phone


class ParentSearchView(LoginRequiredMixin, AdminTestMixin, View):
    """
    Recherche AJAX des parents uniquement. Retourne le partial HTML.
    """

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        student_id = request.GET.get("student_id", "")

        parents = CustomUser.objects.none()
        if query:
            parents = (
                CustomUser.objects.filter(role="parent")
                .filter(
                    Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(phone_number__icontains=query)
                )
                .order_by("first_name", "last_name")
            )

        context = {
            "parents": parents,
            "student_id": student_id,
            "query": query,
        }
        html = render_to_string(
            "users/partials/_parent_cards.html", context, request=request
        )
        return JsonResponse({"html": html})


def link_callback(uri, rel):
    """
    Convertit les URI HTML (ex: /static/...) en chemins absolus pour xhtml2pdf
    """
    # Cherche le fichier dans les staticfiles
    result = finders.find(uri.replace(settings.STATIC_URL, ""))
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        return os.path.realpath(result[0])

    # Si c'est une URL absolue (http:// ou https://), retourne tel quel
    if uri.startswith("http://") or uri.startswith("https://"):
        return uri

    # Sinon essaie dans STATIC_ROOT
    return os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
