from django.contrib.auth.mixins import UserPassesTestMixin

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View


class AdminTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin


class RoleBasedLoginRequiredMixin(View):
    """
    Mixin à ajouter aux CBV pour rediriger vers la bonne page de login si l'utilisateur n'est pas connecté.
    """

    @method_decorator
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            path = request.path

            if path.startswith("/teachers/"):
                return redirect(f"{reverse('attendance:request-otp')}?next={path}")
            else:
                return redirect(f"{reverse('users:login')}?next={path}")
        return super().dispatch(request, *args, **kwargs)
