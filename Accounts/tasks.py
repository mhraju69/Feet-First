import logging
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTP, AccountDeletionRequest
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

logger = logging.getLogger(__name__)

@shared_task
def send_otp_email_task(email, otp_code, task, user_display_name):
    subject = "Feet First OTP Verification"

    # Render HTML template
    html_content = render_to_string("email/otp_email.html", {
        "otp": otp_code,
        "task": task or "Verification",
        "user": user_display_name,
    })

    # Plain text fallback
    text_content = f"""
    Your OTP Code From Feet First for {task or ''} is: {otp_code}
    This OTP is valid for 3 minutes.
    If you did not request this, please ignore this email.
    """

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def cleanup_expired_tokens():
    """
    Remove expired tokens from both OutstandingToken and BlacklistedToken tables.
    """
    now = timezone.now()

    # Remove expired BlacklistedTokens
    expired_blacklist = BlacklistedToken.objects.filter(token__expires_at__lt=now)
    blacklist_count = expired_blacklist.count()
    expired_blacklist.delete()

    # Remove expired OutstandingTokens
    expired_outstanding = OutstandingToken.objects.filter(expires_at__lt=now)
    outstanding_count = expired_outstanding.count()
    expired_outstanding.delete()

    logger.info(f"Expired cleanup done: {blacklist_count} blacklisted tokens removed, "
                f"{outstanding_count} outstanding tokens removed.")
    
@shared_task
def cleanup_expired_otps():
    """
    Remove expired OTP entries from the database.
    """
    now = timezone.now()
    expired_otps = OTP.objects.filter(created_at__lt=now - timedelta(minutes=10))
    count = expired_otps.count()
    expired_otps.delete()
    logger.info(f"Expired OTP cleanup done: {count} OTPs removed.")

@shared_task
def cleanup_old_deletion_requests():
    """
    Delete AccountDeletionRequest records that were confirmed
    more than 30 days ago.
    """
    threshold_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = AccountDeletionRequest.objects.filter(
        deleted_at__lte=threshold_date
    ).delete()
    logger.info(f"Deleted {deleted_count} old deletion requests.")
