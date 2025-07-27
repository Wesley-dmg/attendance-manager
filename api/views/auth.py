from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from api.utils import set_otp_for_user
from api.serializers.auth import OTPRequestSerializer, OTPVerifySerializer

User = get_user_model()


class RequestOTPView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            try:
                user = User.objects.get(phone_number=phone, role="teacher")
                set_otp_for_user(user)
                return Response({"message": "OTP envoyé via WhatsApp"}, status=200)
            except User.DoesNotExist:
                return Response(
                    {"error": "Numéro introuvable ou non autorisé"}, status=404
                )
        return Response(serializer.errors, status=400)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            otp = serializer.validated_data["otp"]
            try:
                user = User.objects.get(phone_number=phone, role="teacher")
                if not user.otp_code or not user.otp_code_expiry:
                    return Response({"error": "Aucun OTP généré."}, status=400)
                if timezone.now() > user.otp_code_expiry:
                    return Response({"error": "OTP expiré."}, status=401)
                if user.otp_code != otp:
                    return Response({"error": "Code invalide."}, status=401)

                # Auth OK → Reset OTP et retour tokens
                user.otp_code = None
                user.otp_code_expiry = None
                user.save(update_fields=["otp_code", "otp_code_expiry"])

                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user": {
                            "id": user.id,
                            "name": user.get_full_name(),
                            "phone": user.phone_number,
                        },
                    },
                    status=200,
                )

            except User.DoesNotExist:
                return Response({"error": "Utilisateur introuvable"}, status=404)
        return Response(serializer.errors, status=400)


class ResendOTPView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            try:
                user = User.objects.get(phone_number=phone, role="teacher")
                if (
                    user.otp_code
                    and user.otp_code_expiry
                    and timezone.now() < user.otp_code_expiry
                ):
                    otp = user.otp_code
                else:
                    otp = set_otp_for_user(user)
                return Response({"message": "OTP renvoyé via WhatsApp"}, status=200)
            except User.DoesNotExist:
                return Response(
                    {"error": "Numéro introuvable ou non autorisé"}, status=404
                )
        return Response(serializer.errors, status=400)
