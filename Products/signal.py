from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def create_favorite_for_new_user(sender, instance, created, **kwargs):
    if created and instance.role == 'customer':
        Favorite.objects.create(user=instance)
    if created and instance.role == 'partner':
        ApprovedPartnerProduct.objects.create(partner=instance)

