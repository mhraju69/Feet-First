from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string

def send_email_view(request):
    # Your logic to get form data
    context = {
        'email': 'sender@example.com',
        'sub': 'Your Subject Here',
        'message': 'Your message content here',
        'time': 'November 3, 2023, 2:30 PM'  # Format as needed
    }
    
    # Render the HTML template
    html_message = render_to_string('email_template.html', context)
    
    # Create and send email
    email = EmailMessage(
        subject=context['sub'],
        body=html_message,
        from_email='noreply@feetfirst.com',
        to=['recipient@example.com'],
    )
    email.content_subtype = 'html'  # Set content to HTML
    email.send()
    
    return HttpResponse('Email sent successfully')