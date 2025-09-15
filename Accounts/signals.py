# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from Products.models import Favourite

# User = get_user_model()

# @receiver(post_save, sender=User)
# def create_favourite_for_new_user(sender, instance, created, **kwargs):
#     if created:
#         # Create a Favourite instance for the new user if not exists
#         Favourite.objects.get_or_create(user=instance)