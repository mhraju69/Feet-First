from django.db import models

# Create your models here.
class AvailableSize(models.Model):
    size = models.CharField(max_length=10, unique=True)
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.size 
    
class Category(models.Model):
    name_de = models.CharField(max_length=200)
    name_it= models.CharField(max_length=200)
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg')

    def __str__(self):
        return self.name_de
    
class SubCategory(models.Model):    
    name_de = models.CharField(max_length=200)
    name_it= models.CharField(max_length=200)
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='subcategory')

    def __str__(self):
        return self.name_de 
    
class Product(models.Model):
    name_de = models.CharField(max_length=200)
    name_it= models.CharField(max_length=200)

    german_description = models.TextField(blank=True, null=True)
    intalian_description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage discount
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    sizes = models.ManyToManyField(AvailableSize)
    widths = models.ManyToManyField(AvailableWidth) 
    toe_type = models.CharField(max_length=100, blank=True, null=True)
    heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    arch_support = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_de 