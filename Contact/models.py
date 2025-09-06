from django.db import models

# Create your models here.

class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='Sending time')
    read = models.BooleanField(default=False,verbose_name='Mark as read')

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        
    def __str__(self):
        return self.email    