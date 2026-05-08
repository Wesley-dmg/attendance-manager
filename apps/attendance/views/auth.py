from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect
from apps.attendance.forms.auth import RequestOTPForm, VerifyOTPForm
from apps.attendance.utils import set_otp_for_user
from apps.home.utils import send_custom_message

User = get_user_model()


class RequestOTPView(FormView):
    template_name = "attendance/auth/request_otp.html"
    form_class = RequestOTPForm

    def dispatch(self, request, *args, **kwargs):
        # Si l'utilisateur est déjà connecté → redirige vers le dashboard
        if request.user.is_authenticated:
            return redirect("/teachers/dashboard/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]

        try:
            user = User.objects.get(phone_number=phone, role__name="teacher")
        except User.DoesNotExist:
            form.add_error("phone", "Numéro introuvable ou non autorisé.")
            return self.form_invalid(form)

        set_otp_for_user(user)  # Génère et stocke un OTP
        self.request.session["phone"] = phone

        next_url = self.request.GET.get("next", "/teachers/dashboard/")
        return redirect(f"{reverse('attendance:verify-otp')}?next={next_url}")


class VerifyOTPView(FormView):
    template_name = "attendance/auth/verify_otp.html"
    form_class = VerifyOTPForm

    def dispatch(self, request, *args, **kwargs):
        # Si l'utilisateur est déjà connecté → redirige vers le dashboard
        if request.user.is_authenticated:
            return redirect("/teachers/dashboard/")
        return super().dispatch(request, *args, **kwargs)

    def get_phone(self):
        return self.request.session.get("phone") or self.request.GET.get("phone")

    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial["phone"] = self.get_phone()
    #     return initial

    def get_initial(self):
        initial = super().get_initial()
        phone = self.get_phone()
        initial["phone"] = phone

        # Récupérer l'utilisateur correspondant
        if phone:
            user = User.objects.filter(
                phone_number__endswith=phone[-9:], role__name="teacher"
            ).first()
            if (
                user
                and hasattr(user, "teacherprofile")
                and user.teacherprofile.otp_code
            ):
                # Pré-remplir le champ code avec l'OTP stocké
                initial["code"] = user.teacherprofile.otp_code

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["phone"] = self.get_phone()
        return context

    def form_valid(self, form):
        phone = self.get_phone()

        if not phone:
            form.add_error("code", "Aucun numéro de téléphone trouvé.")
            return self.form_invalid(form)

        code = form.cleaned_data["code"]
        user = User.objects.filter(
            phone_number__endswith=phone[-9:], role__name="teacher"
        ).first()

        if not user:
            form.add_error("code", "Utilisateur introuvable.")
            return self.form_invalid(form)

        if not user.teacherprofile.is_otp_valid(code):
            form.add_error("code", "Code incorrect ou expiré.")
            return self.form_invalid(form)

        if not user.teacherprofile.otp_code or user.teacherprofile.otp_code != code:
            form.add_error("code", "Code incorrect ou expiré.")
            return self.form_invalid(form)

        # Authentifie l'utilisateur
        login(self.request, user)

        # Redirection vers l'URL suivante ou tableau de bord par défaut
        next_url = self.request.GET.get("next", "/teachers/dashboard/")
        return redirect(next_url)

    def form_invalid(self, form):
        print("Formulaire OTP invalide")
        return super().form_invalid(form)
