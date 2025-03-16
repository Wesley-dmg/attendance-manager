from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_test(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin:  # Vérifie si c'est un admin
            raise PermissionDenied("Vous devez être administrateur pour accéder à cette page.")
        return func(request, *args, **kwargs)
    return wrapper
