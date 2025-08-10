from django.core.exceptions import PermissionDenied
from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse


def admin_test(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:  # Vérifie si c'est un admin
            raise PermissionDenied(
                "Vous devez être administrateur pour accéder à cette page."
            )
        return func(request, *args, **kwargs)

    return wrapper


def role_based_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            path = request.path

            # Redirections intelligentes
            if path.startswith("/teachers/"):
                return redirect(
                    f"{reverse('attendance:request-otp')}?next={request.path}"
                )
            else:
                return redirect(f"{reverse('users:login')}?next={request.path}")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
