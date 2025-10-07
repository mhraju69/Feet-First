import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
User = get_user_model()
from cloudinary_storage.storage import MediaCloudinaryStorage
from Accounts.models import *
from Others.models import Ques, Ans
from Brands.models import Brand

# Create your models here.

class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    hex_code = models.CharField(max_length=7, help_text="Hex color code, e.g. #FFFFFF")
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.color} ({self.hex_code})"

class Category(models.TextChoices):
    EVERYDAY_SHOES = "everyday-shoes", "Everyday Shoes"
    SPORTS_SHOES = "sports-shoes", "Sports Shoes"

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
    MOUNTAIN_TREKKING_SHOES = "mountain-trekking-shoes", "Mountain Trekking Shoes"

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
    
class Color(models.Model):
    color = models.CharField(max_length=20, unique=True,verbose_name='Primary Color Name')
    hex_code = models.CharField(max_length=7, help_text="Hex color code, e.g. #FFFFFF")
    details = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.color} ({self.hex_code})"

class Category(models.TextChoices):
    EVERYDAY_SHOES = "everyday-shoes", "Everyday Shoes"
    SPORTS_SHOES = "sports-shoes", "Sports Shoes"

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
    MOUNTAIN_TREKKING_SHOES = "mountain-trekking-shoes", "Mountain Trekking Shoes"

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

class Product(models.Model):
    partner = models.ForeignKey(
        User,
        limit_choices_to={'role': 'partner'},
        related_name='products',
        on_delete=models.CASCADE
    )

    # Basic info
    name = models.CharField(max_length=200, verbose_name='Name')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="product_brand")
    description = models.TextField()

    # Category/Subcategory
    main_category = models.CharField(max_length=50, choices=Category.choices)
    sub_category = models.CharField(max_length=50, choices=SubCategory.choices, null=True, blank=True)
    sizes = models.ManyToManyField(SizeTable, related_name="products")
    gender = models.TextField(max_length=20, choices=(('male','Male'),('female','Female')))
        
    # Width & Toe box
    width = models.IntegerField(choices=Width.choices, default=Width.NORMAL)
    toe_box = models.CharField(max_length=10, choices=ToeBox.choices, default=ToeBox.NORMAL)

    # Extra info
    technical_data = models.TextField(blank=True, null=True, help_text='Add data as KEY : Value , one per line !')
    further_information = models.TextField(blank=True, null=True)
    
    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    colors = models.ManyToManyField("Color", help_text="Type name to search color")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    # --- IMPROVED MATCHING LOGIC ---
    def match_with_scan(self, scan):
        """
        Enhanced matching algorithm with better scoring and size recommendations.
        Returns detailed match information including multiple size options.
        """
        if not scan:
            return {
                "score": 0,
                "recommended_sizes": [],
                "fit_analysis": {},
                "warnings": ["No foot scan data available"]
            }

        # Use the larger foot for sizing (industry standard)
        foot_length = scan.max_length()
        foot_width = scan.max_width()
        
        # Initialize scoring components
        score_components = {
            'length': 0,
            'width': 0,
            'toe_box': 0,
            'gender': 0,
        }
        
        warnings = []
        size_recommendations = []
        
        # --- 1. LENGTH MATCHING (40% weight) ---
        # Shoe should be 10-15mm longer than foot for comfort
        IDEAL_TOE_SPACE = 12  # mm
        MIN_TOE_SPACE = 8
        MAX_TOE_SPACE = 18
        
        all_sizes = []
        for size_table in self.sizes.all():
            for size in size_table.sizes.all():
                all_sizes.append({
                    'size': size,
                    'table': size_table,
                    'min_length': size.insole_min_mm,
                    'max_length': size.insole_max_mm,
                    'avg_length': (size.insole_min_mm + size.insole_max_mm) / 2
                })
        
        if not all_sizes:
            warnings.append("No size data available for this product")
            return {
                "score": 0,
                "recommended_sizes": [],
                "fit_analysis": {},
                "warnings": warnings
            }
        
        # Find best fitting sizes
        best_length_score = 0
        
        for size_info in all_sizes:
            # Calculate required insole length (foot + toe space)
            ideal_insole = foot_length + IDEAL_TOE_SPACE
            min_acceptable = foot_length + MIN_TOE_SPACE
            max_acceptable = foot_length + MAX_TOE_SPACE
            
            size_avg = size_info['avg_length']
            
            # Check if size fits within acceptable range
            if min_acceptable <= size_avg <= max_acceptable:
                # Calculate how close to ideal
                deviation = abs(size_avg - ideal_insole)
                
                if deviation <= 2:
                    length_score = 1.0
                    fit_type = "perfect"
                elif deviation <= 4:
                    length_score = 0.95
                    fit_type = "excellent"
                elif deviation <= 6:
                    length_score = 0.85
                    fit_type = "good"
                else:
                    length_score = 0.70
                    fit_type = "acceptable"
                
                # Determine fit preference
                if size_avg < ideal_insole:
                    fit_note = "snug fit"
                elif size_avg > ideal_insole:
                    fit_note = "roomy fit"
                else:
                    fit_note = "true to size"
                
                size_recommendations.append({
                    'size_value': size_info['size'].value,
                    'size_type': size_info['size'].type,
                    'size_table': size_info['table'].name,
                    'fit_type': fit_type,
                    'fit_note': fit_note,
                    'score': length_score,
                    'insole_length': f"{size_info['min_length']}-{size_info['max_length']}mm"
                })
                
                best_length_score = max(best_length_score, length_score)
            else:
                # Size doesn't fit well
                if size_avg < min_acceptable:
                    diff = min_acceptable - size_avg
                    if diff <= 5:
                        length_score = 0.5
                    elif diff <= 10:
                        length_score = 0.3
                    else:
                        length_score = 0.0
                else:  # size_avg > max_acceptable
                    diff = size_avg - max_acceptable
                    if diff <= 5:
                        length_score = 0.6
                    elif diff <= 10:
                        length_score = 0.4
                    else:
                        length_score = 0.0
        
        score_components['length'] = best_length_score * 40
        
        # --- 2. WIDTH MATCHING (35% weight) ---
        foot_width_category = scan.width_category()
        product_width = self.width
        
        width_diff = abs(foot_width_category - product_width)
        
        if width_diff == 0:
            width_score = 1.0
            width_match = "Perfect width match"
        elif width_diff == 1:
            width_score = 0.80
            if foot_width_category > product_width:
                width_match = "Slightly narrower than ideal"
                warnings.append("Consider trying a wide version if available")
            else:
                width_match = "Slightly wider than ideal"
        elif width_diff == 2:
            width_score = 0.50
            if foot_width_category > product_width:
                width_match = "May feel tight"
                warnings.append("This shoe may feel narrow for your foot")
            else:
                width_match = "May feel loose"
        elif width_diff == 3:
            width_score = 0.25
            width_match = "Poor width match"
            warnings.append("Width mismatch - not recommended")
        else:
            width_score = 0.0
            width_match = "Incompatible width"
            warnings.append("Strong width mismatch - please choose another model")
        
        score_components['width'] = width_score * 35
        
        # --- 3. TOE BOX MATCHING (15% weight) ---
        foot_toe_box = scan.toe_box_category()
        product_toe_box = self.toe_box
        
        if foot_toe_box == product_toe_box:
            toe_box_score = 1.0
            toe_box_match = "Perfect toe box match"
        elif (foot_toe_box == "normal" and product_toe_box in ["narrow", "wide"]) or \
             (product_toe_box == "normal" and foot_toe_box in ["narrow", "wide"]):
            toe_box_score = 0.70
            toe_box_match = "Acceptable toe box"
        else:
            toe_box_score = 0.30
            toe_box_match = "Toe box mismatch"
            if foot_toe_box == "wide" and product_toe_box == "narrow":
                warnings.append("Toe box may feel cramped")
            elif foot_toe_box == "narrow" and product_toe_box == "wide":
                warnings.append("Toe box may feel too spacious")
        
        score_components['toe_box'] = toe_box_score * 15
        
        # --- 4. GENDER MATCHING (10% weight) ---
        # This is a soft match - doesn't disqualify but affects score
        user_gender = getattr(scan.user, 'gender', None)
        
        if user_gender and user_gender.lower() == self.gender.lower():
            gender_score = 1.0
        else:
            gender_score = 0.5  # Still acceptable, just noted
        
        score_components['gender'] = gender_score * 10
        
        # --- CALCULATE TOTAL SCORE ---
        total_score = sum(score_components.values())
        
        # Sort size recommendations by score
        size_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit to top 3 recommendations
        size_recommendations = size_recommendations[:3]
        
        # Additional warnings based on total score
        if total_score < 50:
            warnings.append("Low compatibility - consider other models")
        elif total_score < 70:
            warnings.append("Moderate fit - try before buying if possible")
        
        # Build detailed fit analysis
        fit_analysis = {
            'length_match': f"{score_components['length']:.1f}/40",
            'width_match': width_match,
            'width_score': f"{score_components['width']:.1f}/35",
            'toe_box_match': toe_box_match,
            'toe_box_score': f"{score_components['toe_box']:.1f}/15",
            'gender_score': f"{score_components['gender']:.1f}/10",
            'foot_measurements': {
                'length': f"{foot_length:.1f}mm",
                'width': f"{foot_width:.1f}mm",
                'width_category': Width(foot_width_category).label,
                'toe_box_category': foot_toe_box
            }
        }
        
        return {
            "score": round(total_score, 1),
            "recommended_sizes": size_recommendations,
            "fit_analysis": fit_analysis,
            "warnings": warnings if warnings else ["Good match!"]
        }


class FootScan(models.Model):   
    user = models.OneToOneField(
        User,
        limit_choices_to={'role': 'customer'},
        on_delete=models.CASCADE,
        related_name="foot_scans",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Foot length (mm)
    left_length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Left foot length in mm")
    right_length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Right foot length in mm")

    # Foot width (mm)
    left_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Left foot width in mm")
    right_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Right foot width in mm")

    # Arch Index (for future insole recommendation)
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
        """Returns the bigger foot length (used for shoe sizing)."""
        return float(max(self.left_length, self.right_length))

    def max_width(self):
        """Returns the wider foot (used for shoe sizing)."""
        return float(max(self.left_width, self.right_width))

    # --- IMPROVED Category mappings ---
    def width_category(self):
        """
        Improved width categorization using width-to-length ratio.
        More accurate than absolute width values.
        Returns: 0=Narrow, 1=Narrow-Normal, 2=Normal, 3=Normal-Wide, 4=Wide
        """
        length = self.max_length()
        width = self.max_width()
        
        # Calculate width-to-length ratio (typical range: 0.35 - 0.45)
        ratio = width / length if length > 0 else 0
        
        # Refined thresholds based on biomechanical research
        if ratio < 0.37:
            return 0  # Narrow
        elif ratio < 0.39:
            return 1  # Narrow-Normal
        elif ratio < 0.41:
            return 2  # Normal
        elif ratio < 0.43:
            return 3  # Normal-Wide
        else:
            return 4  # Wide

    def toe_box_category(self):
        """
        Improved toe box categorization.
        Returns: "narrow", "normal", "wide"
        """
        length = self.max_length()
        width = self.max_width()
        
        # Use ratio for better accuracy
        ratio = width / length if length > 0 else 0
        
        if ratio < 0.38:
            return "narrow"
        elif ratio < 0.42:
            return "normal"
        else:
            return "wide"
    
    def get_width_label(self):
        """Get human-readable width label."""
        return Width(self.width_category()).label
    
    def get_foot_type(self):
        """Determine overall foot type for better recommendations."""
        arch_avg = None
        if self.left_arch_index and self.right_arch_index:
            arch_avg = (float(self.left_arch_index) + float(self.right_arch_index)) / 2
        
        width_cat = self.width_category()
        
        foot_type = []
        
        # Width type
        if width_cat <= 1:
            foot_type.append("narrow")
        elif width_cat >= 3:
            foot_type.append("wide")
        else:
            foot_type.append("average width")
        
        # Arch type (if available)
        if arch_avg:
            if arch_avg < 0.21:
                foot_type.append("high arch")
            elif arch_avg > 0.26:
                foot_type.append("flat")
            else:
                foot_type.append("normal arch")
        
        return ", ".join(foot_type)

    def __str__(self):
        return f"FootScan for {self.user.email} ({self.get_foot_type()})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/',storage=MediaCloudinaryStorage(),blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
class Question(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_qna")
    question = models.ForeignKey(Ques, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Ans)

    def __str__(self):
        return f"{self.product.name} - {self.question.Question}"
    
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
    
