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
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage discount
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    available_sizes = models.JSONField(default=list, blank=True)  # e.g. ["S", "M", "L"]
    available_widths = models.JSONField(default=list, blank=True)  # e.g. ["Narrow", "Regular", "Wide"]
    toe_type = models.CharField(max_length=100, blank=True, null=True)
    heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    arch_support = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name