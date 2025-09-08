import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage,RawMediaCloudinaryStorage

# Create your models here.
class Size(models.Model):
    size = models.CharField(max_length=10, unique=True)
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.size

class Width(models.Model):
    width = models.CharField(max_length=20, unique=True)
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.width
    
class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    code = models.CharField(max_length=20, unique=True,verbose_name='Color Hex Code')
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.color}"

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

    partner = models.ForeignKey(User, limit_choices_to={'role':'partner'}, related_name='product', on_delete=models.CASCADE)

    name_de = models.CharField(max_length=200,verbose_name='Name (German)')
    name_it= models.CharField(max_length=200,verbose_name='Name (Italian)')

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    details_de = models.TextField(blank=True, null=True,verbose_name='Details (German)')
    details_it = models.TextField(blank=True, null=True,verbose_name='Details (Italian)')

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True,blank=True)  
    stock_quantity = models.PositiveIntegerField(default=0)
    brand = models.CharField(max_length=255, blank=True, null=True)
    sizes = models.ManyToManyField(Size)
    widths = models.ManyToManyField(Width)
    colors = models.ManyToManyField(Color)
    toe_type = models.CharField(max_length=100, blank=True, null=True)
    heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    arch_support = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_de 



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', storage=MediaCloudinaryStorage())
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name_de}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Only users with role='customer' can be selected
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'customer'},  # <- This restricts the admin dropdown
        related_name='orders'
    )

    partner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'partner'},  # restrict partner selection
        related_name='partner_orders'
    )

    products = models.ManyToManyField(Product, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"

    def clean(self):
        # Extra validation if needed
        if self.customer.role != 'customer':
            raise ValidationError("Selected user must have role 'customer'.")
        if self.partner.role != 'partner':
            raise ValidationError("Selected user must have role 'partner'.")

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount
        total = sum([p.price for p in self.products.all()]) if self.products.exists() else 0
        self.total_amount = total
        super().save(*args, **kwargs)
    @staticmethod
    def generate_order_number():
        """
        Generates a fun, unique order number like: ORD-5F8A3C
        """
        return f"ORD-{uuid.uuid4().hex[:6].upper()}"

class PdfFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pdf_files")
    pdf_file = models.FileField(upload_to='foot_scans_pdf/',storage=RawMediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF File for {self.user.email} uploaded at {self.uploaded_at}"