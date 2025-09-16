import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage,RawMediaCloudinaryStorage
from math import fabs
from Accounts.models import *

# Create your models here.

class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.color

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

class Width(models.IntegerChoices):
    NARROW = 0, "Narrow"
    NARROW_NORMAL = 1, "Narrow-Normal"
    NORMAL = 2, "Normal"
    NORMAL_WIDE = 3, "Normal-Wide"
    WIDE = 4, "Wide"

class ToeBox(models.TextChoices):
    NARROW = "narrow", "Narrow"
    NORMAL = "normal", "Normal"
    WIDE = "wide", "Wide"

class SizeSystem(models.TextChoices):
    EU = "EU", "European"
    USM = "USM", "US Men"
    USW = "USW", "US Women"

class Size(models.Model):
    type = models.CharField(max_length=3, choices=SizeSystem.choices)
    value = models.CharField(max_length=5, help_text="e.g. 40, 40.5, 40¾")
    insole_min_mm = models.IntegerField()
    insole_max_mm = models.IntegerField()

    def __str__(self):
        return f"{self.type} {self.value} ({self.insole_min_mm}-{self.insole_max_mm} mm)"

class Product(models.Model):
    partner = models.ForeignKey(
        User,
        limit_choices_to={'role': 'partner'},
        related_name='products',
        on_delete=models.CASCADE
    )
    

    # Basic info
    name = models.CharField(max_length=200, verbose_name='Name')
    brand = models.CharField(max_length=255)
    description = models.TextField()

    # Category/Subcategory
    main_category = models.CharField(max_length=50, choices=Category.choices)
    sub_category = models.CharField(max_length=50, choices=SubCategory.choices, null=True, blank=True)

    # Sizes
    sizes = models.ManyToManyField(Size, related_name="products")

    gender = models.TextField(max_length=20,choices=(('male','Male'),('female','Female')))
    # Width & Toe box
    width = models.IntegerField(choices=Width.choices, default=Width.NORMAL)
    toe_box = models.CharField(max_length=10, choices=ToeBox.choices, default=ToeBox.NORMAL)

    # Extra info
    technical_data = models.TextField(blank=True, null=True,help_text='Add data as KEY : Value , one per line !')
    further_information = models.TextField(blank=True,null=True)

    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    colors = models.ManyToManyField("Color", help_text="Type name to search color")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.name}"

    # --- MATCHING LOGIC ---
    def match_with_scan(self, scan):

        score = 0
        # --- LENGTH MATCH (50%) ---
        # Pick the closest size by insole length
        avg_foot_length = scan.average_length()
        best_size = None
        score_length = 0 
        best_match = 0
        for size in self.sizes.all():
            if size.insole_min_mm <= avg_foot_length <= size.insole_max_mm:
                best_match = 1.0  # perfect
            else:
                diff = min(abs(avg_foot_length - size.insole_min_mm),
                           abs(avg_foot_length - size.insole_max_mm))
                if diff <= 4:
                    best_match = 1.0
                elif diff <= 8:
                    best_match = 0.8
                elif diff <= 12:
                    best_match = 0.6
                elif diff <= 16:
                    best_match = 0.4
                elif diff <= 20:
                    best_match = 0.2
                else:
                    best_match = 0.0
            if best_match > score:
                score_length = best_match   
                best_size = size 
        score += (score_length * 50)

        # --- WIDTH MATCH (30%) ---
        diff_width = abs(scan.width_category() - self.width)
        if diff_width == 0:
            width_score = 1.0
        elif diff_width == 1:
            width_score = 0.75
        elif diff_width == 2:
            width_score = 0.5
        elif diff_width == 3:
            width_score = 0.25
        else:
            width_score = 0.0
        score += (width_score * 30)

        # --- TOE BOX MATCH (20%) ---
        toe_score = 1.0 if scan.toe_box_category() == self.toe_box else 0.0 
        score += (toe_score * 20)

        return {
        "score": round(score, 2),
        "recommended_size": best_size.value if best_size else None,}
    
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

    # Foot width (mm)
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
        """Returns average length of both feet in mm."""
        return float((self.left_length + self.right_length) / 2)

    def average_width(self):
        """Returns average width of both feet in mm."""
        return float((self.left_width + self.right_width) / 2)

    def max_length(self):
        """Returns the bigger foot length (important for shoe fitting)."""
        return float(max(self.left_length, self.right_length))

    def max_width(self):
        """Returns the wider foot (important for shoe fitting)."""
        return float(max(self.left_width, self.right_width))

    # --- Category mappings ---
    def width_category(self):
        """
        Convert actual foot width (mm) into width category.
        Returns one of: 0=Narrow, 1=Narrow-Normal, 2=Normal, 3=Normal-Wide, 4=Wide
        """
        w = self.max_width()

        if w < 85:       # adjust thresholds with real data
            return 0
        elif w < 95:
            return 1
        elif w < 105:
            return 2
        elif w < 115:
            return 3
        else:
            return 4

    def toe_box_category(self):
        """
        Convert forefoot width to toe box category.
        Returns one of: "narrow", "normal", "wide"
        """
        w = self.max_width()

        if w < 90:       # adjust thresholds with biomechanical data
            return "narrow"
        elif w < 110:
            return "normal"
        else:
            return "wide"

    def __str__(self):
        return f"FootScan #{self.id} for {self.user.email}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', storage=MediaCloudinaryStorage())
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
