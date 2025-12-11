import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage
from Accounts.models import *
from Brands.models import Brand

# Create your models here.

class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    hex_code = models.CharField(max_length=7, help_text="Hex color code, e.g. #FFFFFF")
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.color} ({self.hex_code})"

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name
    
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

class SizeTable(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="size_brand")
    name = models.CharField(max_length=100, help_text="e.g. Standard , Wide")
    def __str__(self):
        return f"{self.brand.name} - {self.name}"
    class Meta:
        unique_together = ('brand', 'name')
    
class Size(models.Model):
    table = models.ForeignKey(
        SizeTable,
        related_name="sizes",
        on_delete=models.CASCADE
    )
    type = models.CharField(max_length=3, choices=SizeSystem.choices)
    value = models.CharField(max_length=5, help_text="e.g. 40, 40.5, 40¾")
    insole_min_mm = models.IntegerField()
    insole_max_mm = models.IntegerField()

    def __str__(self):
        return f"{self.type} {self.value}"
    
    class Meta:
        ordering = ['type', 'insole_min_mm']

class Features(models.Model):
    image = models.ImageField(upload_to='products/',storage=MediaCloudinaryStorage(),help_text="Image size should be less than 1MB",blank=True,null = True)
    title = models.CharField(max_length=50)
    details = models.TextField()

    def __str__(self):
        return self.title

class Product(models.Model):

    # Basic info
    name = models.CharField(max_length=200, verbose_name='Name')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="product_brand")
    description = models.TextField()

    # Category/Subcategory
    main_category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE )
    sub_category = models.ForeignKey(SubCategory, related_name='sub_category', on_delete=models.CASCADE )

    sizes = models.ManyToManyField(SizeTable, related_name="products")
    gender = models.TextField(max_length=20, choices=(('male','Male'),('female','Female'),('unisex','Unisex')))
        
    # Width & Toe box
    width = models.IntegerField(choices=Width.choices, default=Width.NORMAL)
    toe_box = models.CharField(max_length=10, choices=ToeBox.choices, default=ToeBox.NORMAL)

    # Extra info
    technical_data = models.TextField(blank=True, null=True)
    further_information = models.TextField(blank=True, null=True)
    
    # Commerce
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    colors = models.ManyToManyField("Color", help_text="Type name to search color")
    features = models.ManyToManyField(Features, help_text="Type text to search features",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    # --- IMPROVED MATCHING LOGIC ---   
    def match_with_scan(self, scan):
        if not scan:
            return {
                "score": 0,
                "recommended_sizes": [],
                "size_scores": [],
                "fit_analysis": {},
                "warnings": ["No foot scan data available"]
            }

        # Use the larger foot for sizing
        foot_length = scan.max_length()
        foot_width = scan.max_width()
        
        warnings = []
        size_recommendations = []
        all_size_scores = []  # Store scores for ALL sizes
        
        # --- GET ALL SIZES ---
        all_sizes = []
        seen_size_tables = set()
        
        # Use sizes ManyToManyField directly
        for size_table in self.sizes.all():
            if size_table.id in seen_size_tables:
                continue
            seen_size_tables.add(size_table.id)
            
            sizes = size_table.sizes.all()
            for size in sizes:
                all_sizes.append({
                    'size': size,
                    'table': size_table,
                    'min_length': size.insole_min_mm,
                    'max_length': size.insole_max_mm,
                })
        
        if not all_sizes:
            warnings.append("No size data available for this product")
            return {
                "score": 0,
                "recommended_sizes": [],
                "size_scores": [],
                "fit_analysis": {},
                "warnings": warnings
            }
        
        # --- CALCULATE SCORE FOR EACH SIZE ---
        for size_info in all_sizes:
            size_min = size_info['min_length']
            size_max = size_info['max_length']
            size_value = size_info['size'].value
            size_type = size_info['size'].type
            
            # 1. LENGTH SCORING (50%)
            if size_min <= foot_length <= size_max:
                length_score = 1.0  # 100%
            else:
                if foot_length < size_min:
                    deviation = size_min - foot_length
                else:
                    deviation = foot_length - size_max
                
                if deviation <= 4:
                    length_score = 0.8  # 80%
                elif deviation <= 8:
                    length_score = 0.6  # 60%
                elif deviation <= 12:
                    length_score = 0.4  # 40%
                elif deviation <= 16:
                    length_score = 0.2  # 20%
                else:
                    length_score = 0.0  # 0%
            
            # 2. WIDTH SCORING (30%)
            foot_width_category = scan.width_category()
            product_width = self.width
            width_diff = abs(foot_width_category - product_width)
            
            if width_diff == 0:
                width_score = 1.0   # 100%
            elif width_diff == 1:
                width_score = 0.75  # 75%
            elif width_diff == 2:
                width_score = 0.5   # 50%
            elif width_diff == 3:
                width_score = 0.25  # 25%
            else:
                width_score = 0.0   # 0%
            
            # 3. TOE BOX SCORING (20%)
            foot_toe_box = scan.toe_box_category()
            product_toe_box = self.toe_box
            
            if foot_toe_box == product_toe_box:
                toe_box_score = 1.0  # 100%
            else:
                toe_box_score = 0.0  # 0%
            
            # CALCULATE TOTAL SCORE FOR THIS SIZE
            total_size_score = (length_score * 50) + (width_score * 30) + (toe_box_score * 20)
            
            # ✅ STORE ONLY SIZE AND SCORE
            size_score_info = {
                "size": f"{size_type} {size_value}",
                "score": round(total_size_score, 1)
            }
            
            all_size_scores.append(size_score_info)
            
            # Also add to recommendations for top 3
            size_rec = {
                'size_value': size_value,
                'size_type': size_type,
                'total_score': round(total_size_score, 1)
            }
            
            size_recommendations.append(size_rec)
        
        # --- FINAL CALCULATIONS ---
        # Sort by score (highest first)
        all_size_scores.sort(key=lambda x: -x['score'])
        size_recommendations.sort(key=lambda x: -x['total_score'])
        
        # Get top 3 recommendations
        top_recommendations = size_recommendations[:3]
        
        # Overall product score = best size score
        overall_score = all_size_scores[0]['score'] if all_size_scores else 0
        
        # Build fit analysis
        fit_analysis = {
            'foot_measurements': {
                'length': f"{foot_length:.1f}mm",
                'width': f"{foot_width:.1f}mm",
                'width_category': Width(scan.width_category()).label,
                'toe_box_category': scan.toe_box_category().capitalize()
            },
            'shoe_specs': {
                'width': Width(self.width).label,
                'toe_box': self.toe_box.capitalize()
            }
        }
        
        return {
            "score": overall_score,  # Overall product score
            "recommended_sizes": top_recommendations,  # Top 3 sizes
            "size_scores": all_size_scores,  # ✅ ONLY size and score for all sizes
            "fit_analysis": fit_analysis,
            "warnings": warnings if warnings else ["Excellent match!"]
        }

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/',storage=MediaCloudinaryStorage(),blank=False, null=False,help_text="Image size should be less than 1MB")
    created_at = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
        
class Favorite(models.Model):
    user = models.OneToOneField(
        User,
        limit_choices_to={'role': 'customer'},
        on_delete=models.CASCADE,
        related_name="favorite"
    )
    products = models.ManyToManyField(
        'Product',
        related_name="favorited_by",
        blank=True
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email}'s favorites"
    
class PartnerProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='partner_prices')
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_prices')
    size = models.ManyToManyField(SizeTable, related_name='partner_product_sizes', help_text="Size table for this product")
    color = models.ManyToManyField(Color, related_name='partner_product_colors', help_text="Color variant for this product")
    price = models.DecimalField(default=0.00,max_digits=10, decimal_places=2, help_text="Partner's custom price for this product")
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Partner's custom discount")
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Partner's stock quantity")
    is_active = models.BooleanField(default=True, help_text="Is this product active for this partner")
    local = models.BooleanField(default=True, help_text="Is this product available locally")
    online = models.BooleanField(default=True, help_text="Is this product available online")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('partner', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.partner.email} - {self.product.name} - ${self.price}"
