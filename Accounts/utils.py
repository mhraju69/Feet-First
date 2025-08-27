
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
def send_otp(email,task=None):
    if not email:
        raise ValueError("Email is required.")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    
    exists = OTP.objects.filter(user=user).exists()
    if  exists:
        OTP.objects.filter(user=user).delete()

    otp = OTP.generate_otp(user)
    subject = 'Feet First OTP Verification'
    message = f"""
        Your OTP Code From Feet First for {task or  "Verification"} is: {otp.otp}
        This OTP is valid for 10 minutes.
        If you did not request this, please ignore this email.
        """

    send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    return True


def verify_otp(email, otp_code):
    otp = OTP.objects.filter(user__email=email, otp=otp_code).first()

    if not otp or otp.created_at + timedelta(minutes=3) < timezone.now():
        otp.delete()    
        return False

    otp.delete()
    return True

