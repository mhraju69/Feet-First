import logging
from .models import *
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .tasks import send_otp_email_task

logger = logging.getLogger(__name__)

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

    # Trigger background task to send email
    send_otp_email_task.delay(email, otp.otp, task, user.name or user.email)

    return {"success": True, "message": f"OTP sent successfully for {task or 'Verification'}."}


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