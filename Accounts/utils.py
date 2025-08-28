
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_otp(email, task=None):
    if not email:
        raise ValueError("Email is required.")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False

    # Remove old OTP if exists
    OTP.objects.filter(user=user).delete()

    # Generate new OTP
    otp = OTP.generate_otp(user)

    subject = "Feet First OTP Verification"

    # Render HTML template (templates/email/otp_email.html)
    html_content = render_to_string("email/otp_email.html", {
        "otp": otp.otp,
        "task": task or "Verification",
        "user": user.name,
    })

    # Plain text fallback (for clients that don’t support HTML)
    text_content = f"""
    Your OTP Code From Feet First for {task or ''} is: {otp.otp}
    This OTP is valid for 3 minutes.
    If you did not request this, please ignore this email.
    """

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return True

# def send_otp(email,task=None):
#     if not email:
#         raise ValueError("Email is required.")
#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         return False
    
#     exists = OTP.objects.filter(user=user).exists()
#     if  exists:
#         OTP.objects.filter(user=user).delete()

#     otp = OTP.generate_otp(user)
#     subject = 'Feet First OTP Verification'
#     message = f"""
#         Your OTP Code From Feet First for {task or  "Verification"} is: {otp.otp}
#         This OTP is valid for 10 minutes.
#         If you did not request this, please ignore this email.
#         """

#     send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [email],
#             fail_silently=False,
#         )
#     return True


def verify_otp(email, otp_code):
    otp = OTP.objects.filter(user__email=email, otp=otp_code).first()

    if not otp:
        return False

    if otp.created_at + timedelta(minutes=3) < timezone.now():
        otp.delete()
        return False
    
    otp.delete()
    return True

