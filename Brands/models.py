from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='brand_images/', storage=MediaCloudinaryStorage(),help_text="Image size should be less than 1MB")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name