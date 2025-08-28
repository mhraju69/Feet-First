
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
        return {"success": False, "message": "User not found."}
    

    otp = OTP.objects.filter(user__email=email).first()
    if otp and not otp.is_expired():
        return {"success": False, "message": "An OTP has already sent. Please check your email."}
    

    # Remove old OTP if exists
    OTP.objects.filter(user=user).delete()

    # Generate new OTP
    otp = OTP.generate_otp(user)

    subject = "Feet First OTP Verification"

    # Render HTML template (templates/email/otp_email.html)
    html_content = render_to_string("email/otp_email.html", {
        "otp": otp.otp,
        "task": task or "Verification",
        "user": user.name or user.email,
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

    return {"success": True, "message": f"OTP sent successfully for {task or 'Verification'}."}



def verify_otp(email, otp_code):
    otp = OTP.objects.filter(user__email=email, otp=otp_code).first()

    if not otp:
        return False
    otp.delete()
    return True

# utils.py
from datetime import timedelta
from django.utils import timezone

def verify_otp(email, otp_code, max_attempts=3, lock_minutes=1):
    try:
        otp_obj = OTP.objects.filter(user__email=email).latest('created_at')
    except OTP.DoesNotExist:
        return {"success": False, "message": "Invalid OTP or email."}

    # Check expiry
    if otp_obj.is_expired():
        return {"success": False, "message": "OTP has expired."}

    # Check attempt limit
    if otp_obj.attempt_count >= max_attempts:
        if otp_obj.last_tried and otp_obj.last_tried + timedelta(minutes=lock_minutes) > timezone.now():
            remaining = int((otp_obj.last_tried + timedelta(minutes=lock_minutes) - timezone.now()).seconds)
            return {"success": False, "message": f"Too many attempts. Try again in {remaining} seconds."}
        else:
            otp_obj.attempt_count = 0  # reset after lock period

    # Verify OTP
    if otp_obj.otp != otp_code:
        otp_obj.attempt_count += 1
        otp_obj.last_tried = timezone.now()
        otp_obj.save()
        attempts_left = max_attempts - otp_obj.attempt_count
        return {"success": False, "message": f"Invalid OTP. You have {attempts_left} attempts left."}

    # OTP verified, activate user & delete OTP
    user = otp_obj.user
    user.is_active = True
    user.save()
    otp_obj.delete()

    return {"success": True, "message": "OTP verified successfully."}
