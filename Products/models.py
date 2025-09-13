import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage,RawMediaCloudinaryStorage
from math import fabs


# Create your models here.

class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    code = models.CharField(max_length=20, unique=True,verbose_name='Color Hex Code')
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.color}  {self.code}"

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
  

# --- ENUM Choices ---
class Category(models.TextChoices):
    EVERYDAY_SHOES = "everyday-shoes", "Everyday Shoes"
    SPORTS_SHOES = "sports-shoes", "Sports Shoes"
    MOUNTAIN_TREKKING_SHOES = "mountain-trekking-shoes", "Mountain Trekking Shoes"

class SubCategory(models.TextChoices):
    RUNNING_SHOES = "running-shoes", "Running Shoes"
    CYCLING_SHOES = "cycling-shoes", "Cycling Shoes"
    HOCKEY_SHOES = "hockey-shoes", "Hockey Shoes"
    SKI_BOOTS = "ski-boots", "Ski Boots"
    BASKETBALL_SHOES = "basketball-shoes", "Basketball Shoes"
    GOLF_SHOES = "golf-shoes", "Golf Shoes"
    FOOTBALL_SHOES = "football-shoes", "Football Shoes"
    TENNIS_SHOES = "tennis-shoes", "Tennis Shoes"
    CLIMBING_SHOES = "climbing-shoes", "Climbing Shoes"
    CASUAL_SNEAKER = "casual-sneaker", "Casual Sneaker"
    ELEGANT_SHOES = "elegant-shoes", "Elegant Shoes"
    COMFORTABLE_SHOES = "comfortable-shoes", "Comfortable Shoes"
    SANDALS = "sandals", "Sandals"
    WORK_SHOES = "work-shoes", "Work Shoes"
    MISCELLANEOUS = "miscellaneous", "Miscellaneous"

class SizeSystem(models.TextChoices):
    EU = "EU", "European"
    US_MEN = "USM", "US Men"
    US_WOMEN = "USW", "US Women"

class WidthCategory(models.IntegerChoices):
    NARROW = 0, "Narrow"
    NARROW_NORMAL = 1, "Narrow-Normal"
    NORMAL = 2, "Normal"
    NORMAL_WIDE = 3, "Normal-Wide"
    WIDE = 4, "Wide"

class ToeBox(models.TextChoices):
    NARROW = "narrow", "Narrow"
    NORMAL = "normal", "Normal"
    WIDE = "wide", "Wide"

# --- PRODUCT MODEL ---
class Product(models.Model):
    # Partner/vendor
    partner = models.ForeignKey(
        User,
        limit_choices_to={'role': 'partner'},
        related_name='products',
        on_delete=models.CASCADE
    )

    # Basic info
    name_de = models.CharField(max_length=200, verbose_name='Name (German)')
    name_it = models.CharField(max_length=200, verbose_name='Name (Italian)')
    brand = models.CharField(max_length=255, blank=True, null=True)

    # Category/Subcategory (fixed or dynamic as needed)
    main_category = models.CharField(max_length=50, choices=Category.choices)
    sub_category = models.CharField(max_length=50, choices=SubCategory.choices, null=True, blank=True)

    # Size info
    size_system = models.CharField(max_length=3, choices=SizeSystem.choices, default=SizeSystem.EU)
    size_value = models.CharField(max_length=10)       # e.g. "40", "40.5", "40¾"
    insole_min_mm = models.IntegerField()
    insole_max_mm = models.IntegerField()

    # Width & Toe
    width_category = models.IntegerField(choices=WidthCategory.choices, default=WidthCategory.NORMAL)
    toe_box = models.CharField(max_length=10, choices=ToeBox.choices, default=ToeBox.NORMAL)

    # --- FOOT MEASUREMENT DATA ---

    # Foot length (millimeters)
    left_foot_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,help_text="Left foot length in mm")
    right_foot_length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,help_text="Right foot length in mm")

    # Foot width (millimeters)
    left_foot_width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,help_text="Left foot width in mm")
    right_foot_width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,help_text="Right foot width in mm")

    # Arch Index (already included for both feet)
    left_arch_index = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    right_arch_index = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Heel Angle
    left_heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,help_text="Left heel angle in degrees")
    right_heel_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,help_text="Right heel angle in degrees")

    # Other attributes
    technical_data = models.TextField(blank=True, null=True, help_text="Technical specs, key: value per line")
    further_information = models.TextField(blank=True, help_text="Weitere Informationen")

    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Colors (optional simple CSV field)
    colors = models.ManyToManyField(Color,max_length=255 , help_text="Type name to search color")

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand or ''} {self.name_de} ({self.size_system} {self.size_value})"

    def match_with_scan(self, scan):
        """
        Compare this Product against a FootScan and return match percentage (0-100).
        """

        score = 0
        weight_total = 0

        # --- LENGTH MATCH (40%) ---
        if self.left_foot_length and self.right_foot_length:
            product_length_mid = float((self.left_foot_length + self.right_foot_length) / 2)
            length_diff = fabs(scan.average_length() - product_length_mid)

            # assume 5mm tolerance = full score, 10mm = 0
            length_match = max(0, 1 - (length_diff / 10))
            score += length_match * 40
            weight_total += 40

        # --- WIDTH MATCH (30%) ---
        if self.left_foot_width and self.right_foot_width:
            product_width_mid = float((self.left_foot_width + self.right_foot_width) / 2)
            width_diff = fabs(scan.average_width() - product_width_mid)

            width_match = max(0, 1 - (width_diff / 10))
            score += width_match * 30
            weight_total += 30

        # --- ARCH INDEX MATCH (20%) ---
        if self.left_arch_index and self.right_arch_index and scan.left_arch_index and scan.right_arch_index:
            product_arch_mid = float((self.left_arch_index + self.right_arch_index) / 2)
            scan_arch_mid = float((scan.left_arch_index + scan.right_arch_index) / 2)

            arch_diff = fabs(scan_arch_mid - product_arch_mid)
            arch_match = max(0, 1 - (arch_diff / 50))  # 50 tolerance
            score += arch_match * 20
            weight_total += 20

        # --- HEEL ANGLE MATCH (10%) ---
        if self.left_heel_angle and self.right_heel_angle and scan.left_heel_angle and scan.right_heel_angle:
            product_heel_mid = float((self.left_heel_angle + self.right_heel_angle) / 2)
            scan_heel_mid = float((scan.left_heel_angle + scan.right_heel_angle) / 2)

            heel_diff = fabs(scan_heel_mid - product_heel_mid)
            heel_match = max(0, 1 - (heel_diff / 10))  # 10° tolerance
            score += heel_match * 10
            weight_total += 10

        # Final percentage
        return round((score / weight_total) * 100, 2) if weight_total > 0 else 0
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', storage=MediaCloudinaryStorage())
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
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

class FootScan(models.Model):
    user = models.ForeignKey(
        User,
        limit_choices_to={'role': 'customer'},
        on_delete=models.CASCADE,
        related_name="foot_scans"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Foot length (mm)
    left_length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Left foot length in mm")
    right_length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Right foot length in mm")

    # Width (mm)
    left_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Left foot width in mm")
    right_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Right foot width in mm")

    # Arch Index (for insole recommendation)
    left_arch_index = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    right_arch_index = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Heel Angle
    left_heel_angle = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                          help_text="Left heel angle in degrees")
    right_heel_angle = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                                           help_text="Right heel angle in degrees")

    # --- Utility Methods ---

    def average_length(self):
        """Returns average length of both feet."""
        return float((self.left_length + self.right_length) / 2)

    def average_width(self):
        """Returns average width of both feet."""
        return float((self.left_width + self.right_width) / 2)

    def max_length(self):
        """Returns the bigger foot (important for shoe fitting)."""
        return float(max(self.left_length, self.right_length))

    def max_width(self):
        """Returns the wider foot."""
        return float(max(self.left_width, self.right_width))

    def __str__(self):
        return f"FootScan #{self.id} for {self.user.email}"
    
