from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage,RawMediaCloudinaryStorage

# Create your models here.
class AvailableSize(models.Model):
    size = models.CharField(max_length=10, unique=True)
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.size 

class AvailableWidth(models.Model):
    width = models.CharField(max_length=20, unique=True)
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.width

class Category(models.Model):
    name_de = models.CharField(max_length=200,verbose_name='Name (German)')
    name_it= models.CharField(max_length=200,verbose_name='Name (Italian)')
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg',storage=MediaCloudinaryStorage())

    def __str__(self):
        return self.name_de
    
class SubCategory(models.Model):    
    name_de = models.CharField(max_length=200,verbose_name='Name (German)')
    name_it= models.CharField(max_length=200,verbose_name='Name (Italian)')
    image = models.ImageField(upload_to='category_images/',default='category_images/default.jpg',storage=MediaCloudinaryStorage())
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='subcategory')

    def __str__(self):
        return self.name_de 
    
class Product(models.Model):
    CATEGORY_CHOICES = [
    ("running-shoes", "Running Shoes"),
    ("cycling-shoes", "Cycling Shoes"),
    ("hockey-shoes", "Hockey Shoes"),
    ("ski-boots", "Ski Boots"),
    ("basketball-shoes", "Basketball Shoes"),
    ("golf-shoes", "Golf Shoes"),
    ("football-shoes", "Football Shoes"),
    ("tennis-shoes", "Tennis Shoes"),
    ("climbing-shoes", "Climbing Shoes"),
    ("casual-sneaker", "Casual Sneaker"),
    ("elegant-shoes", "Elegant Shoes"),
    ("comfortable-shoes", "Comfortable Shoes"),
    ("sandals", "Sandals"),
    ("work-shoes", "Work Shoes"),
    ("miscellaneous", "Miscellaneous"),
]

   
    name_de = models.CharField(max_length=200)
    name_it= models.CharField(max_length=200)

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    details_de = models.TextField(blank=True, null=True)
    details_it = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    sizes = models.ManyToManyField(AvailableSize)
    widths = models.ManyToManyField(AvailableWidth) 
    toe_type = models.CharField(max_length=100, blank=True, null=True)
    heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    arch_support = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_de 
    
class PdfFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pdf_files")
    pdf_file = models.FileField(upload_to='foot_scans_pdf/',storage=RawMediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF File for {self.user.email} uploaded at {self.uploaded_at}"