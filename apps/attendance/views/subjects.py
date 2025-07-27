from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


from django.http import HttpResponse


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/dashboard.html"

    def get(self, request, *args, **kwargs):

        print("Dashboard — user connecté ?", request.user.is_authenticated)
        print("Session key:", request.session.session_key)

        if not request.user.is_authenticated:
            return HttpResponse("Utilisateur non connecté")
        return super().get(request, *args, **kwargs)
