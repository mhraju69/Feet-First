from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactUs

@receiver(post_save, sender=ContactUs)
def send_contact_email(sender, instance, created, **kwargs):
    """
    Signal to send email notification when a new ContactUs message is created
    """
    if created:  # Only trigger for new instances, not updates
        # Prepare email context
        context = {
            'name': instance.name,
            'email': instance.email,
            'subject': instance.subject,
            'message': instance.message,
            'time': instance.created_at.strftime("%B %d, %Y at %I:%M %p"),
            'site_name': 'FeetFirst',  # You can change this to your actual site name
        }
        
        # Render HTML email template
        html_message = render_to_string('email/support_email.html', context)
        
        # Prepare email subject
        email_subject = f"New Contact Message: {instance.subject}"
        
        # Create and send email
        email = EmailMessage(
            subject=email_subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],  # Make sure to set this in your settings
            reply_to=[instance.email],  # So replies go to the original sender
        )
        email.content_subtype = 'html'  # Set content to HTML
        
        try:
            email.send()
            # Optional: Log successful email sending
            print(f"Email sent for support message from {instance.email}")
        except Exception as e:
            # Log the error (you might want to use proper logging here)
            print(f"Failed to send email notification: {str(e)}")