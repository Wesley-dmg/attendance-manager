from django.shortcuts import redirect
from django.urls import reverse


class RedirectIfAuthenticatedMiddleware:
    """
    Si l'utilisateur est déjà connecté et qu'il essaie d'aller sur la page login,
    le rediriger automatiquement vers le dashboard .
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        login_url = reverse("attendance:request-otp")

        dashboard_url = reverse("attendance:dashboard")

        if request.user.is_authenticated and request.path == login_url:
            return redirect(dashboard_url)

        response = self.get_response(request)
        return response
