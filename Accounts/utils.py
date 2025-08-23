
from .models import *
from django.core.mail import send_mail
from django.conf import settings

def send_otp(email):
    if not email:
        raise ValueError("Email is required.")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    otp = OTP.generate_otp(user)
    subject = 'FeetFirst Account Verification'
    message = (
        f'Your OTP Code For FeetFirst Account Verification is: {otp.otp}\n'
    )
    send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    return True