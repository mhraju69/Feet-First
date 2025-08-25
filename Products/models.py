from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='subcategory')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    