from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

def send_whatsapp_message(user, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        response = client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_SANDBOX_NUMBER,
            # to=user.whatsapp_number
            to='whatsapp:+22997064433'

        )
        print(f"[TWILIO] Message envoyé à {user.whatsapp_number} (sid={response.sid})")
        return True, response.sid
    except Exception as e:
        print(f"[ERREUR TWILIO] {e}")
        return False, str(e)

def set_otp_for_user(user, length=6, expiry_minutes=5):
    otp = f"{random.randint(0, 999999):06d}"
    user.otp_code = otp
    user.otp_code_expiry = timezone.now() + timedelta(minutes=expiry_minutes)
    user.save(update_fields=["otp_code", "otp_code_expiry"])

    msg = f"Votre code de connexion est : {otp}. Il expire dans {expiry_minutes} minutes."
    send_whatsapp_message(user, msg)
    return otp
