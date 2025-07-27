from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.utils import timezone

from apps.attendance.forms.auth import RequestOTPForm, VerifyOTPForm
from apps.attendance.utils import set_otp_for_user
from apps.home.utils import send_custom_message

User = get_user_model()


class RequestOTPView(FormView):
    template_name = "attendance/auth/request_otp.html"
    form_class = RequestOTPForm

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]
        try:
            user = User.objects.get(phone_number=phone, role="teacher")
            set_otp_for_user(user)
            # url = (
            #     reverse("attendance:verify-otp")
            #     + f"?phone={phone}&next=/teachers/dashboard/"
            # )

            next_url = self.request.GET.get("next", "/teachers/dashboard/")
            url = f"{reverse('attendance:verify-otp')}?phone={phone}&next={next_url}"

            return redirect(url)
        except User.DoesNotExist:
            form.add_error("phone", "Numéro introuvable ou non autorisé")
            return self.form_invalid(form)


def normalize_phone(phone):
    phone = phone.strip()
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone


class VerifyOTPView(FormView):
    template_name = "attendance/auth/verify_otp.html"
    form_class = VerifyOTPForm

    def get_initial(self):
        phone = self.request.GET.get("phone")
        print(f"Numéro dans get_initial: {phone}")
        return {"phone": self.request.GET.get("phone")}

    def form_valid(self, form):
        phone = normalize_phone(form.cleaned_data["phone"])
        print(f"Numéro dans form_valid: {phone}")
        try:
            print("form_valide")
            phone = form.cleaned_data["phone"]
            otp = form.cleaned_data["otp"]
            user = User.objects.get(phone_number=phone, role="teacher")

            if not user.otp_code or not user.otp_code_expiry:
                form.add_error("otp", "Aucun code généré")
                return self.form_invalid(form)

            if timezone.now() > user.otp_code_expiry:
                form.add_error("otp", "Code OTP expiré")
                return self.form_invalid(form)

            if user.otp_code != otp:
                form.add_error("otp", "Code invalide")
                return self.form_invalid(form)

            user.otp_code = None
            user.otp_code_expiry = None
            user.save(update_fields=["otp_code", "otp_code_expiry"])
            login(self.request, user)

            print(f"Utilisateur connecté ? {self.request.user.is_authenticated}")

            # print avant le message
            print("Avant send_custom_message")
            send_custom_message(self.request, "Connexion réussie.", "success")

            print("Après send_custom_message")

            next_url = self.request.GET.get("next") or reverse("attendance:dashboard")

            print("Redirection vers:", next_url)
            return redirect(next_url)
        except Exception as e:
            print("Erreur dans form_valid:", e)
            import traceback

            traceback.print_exc()
            form.add_error(None, "Une erreur inattendue est survenue.")
            return self.form_invalid(form)
