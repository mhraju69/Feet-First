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
    main_category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE )
    sub_category = models.ForeignKey(SubCategory, related_name='sub_category', on_delete=models.CASCADE )

    # sizes = models.ManyToManyField(SizeTable, related_name="products")
    gender = models.TextField(max_length=20, choices=(('male','Male'),('female','Female')))
        
    # Width & Toe box
    width = models.IntegerField(choices=Width.choices, default=Width.NORMAL)
    toe_box = models.CharField(max_length=10, choices=ToeBox.choices, default=ToeBox.NORMAL)

    # Extra info
    technical_data = models.TextField(blank=True, null=True)
    further_information = models.TextField(blank=True, null=True)
    
    # Commerce
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # stock_quantity = models.PositiveIntegerField(default=0)
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
        
        print(f"🔍 DEBUG: Foot measurements - Length: {foot_length}mm, Width: {foot_width}mm")
        
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
        seen_size_tables = set()
        
        # Get unique size tables through the Quantity relationship
        quantities = self.quantities.select_related('size').all()
        print(f"🔍 DEBUG: Found {quantities.count()} quantity records")
        
        for quantity in quantities:
            size_table = quantity.size
            
            # Avoid processing the same size table multiple times
            if size_table.id in seen_size_tables:
                continue
            seen_size_tables.add(size_table.id)
            
            print(f"🔍 DEBUG: Processing size table: {size_table.name}")
            
            # Get all sizes from this size table
            sizes = size_table.sizes.all()
            print(f"🔍 DEBUG: Size table has {sizes.count()} sizes")
            
            for size in sizes:
                all_sizes.append({
                    'size': size,
                    'table': size_table,
                    'min_length': size.insole_min_mm,
                    'max_length': size.insole_max_mm,
                    'avg_length': (size.insole_min_mm + size.insole_max_mm) / 2
                })
                print(f"🔍 DEBUG: Added size {size.type} {size.value} - {size.insole_min_mm}-{size.insole_max_mm}mm")
        
        if not all_sizes:
            warnings.append("No size data available for this product")
            print("⚠️ DEBUG: No sizes found!")
            return {
                "score": 0,
                "recommended_sizes": [],
                "fit_analysis": {},
                "warnings": warnings
            }
        
        print(f"🔍 DEBUG: Total sizes to evaluate: {len(all_sizes)}")
        
        # Calculate required insole length ranges
        ideal_insole = foot_length + IDEAL_TOE_SPACE
        min_acceptable = foot_length + MIN_TOE_SPACE
        max_acceptable = foot_length + MAX_TOE_SPACE
        
        print(f"🔍 DEBUG: Ideal insole: {ideal_insole}mm, Range: {min_acceptable}-{max_acceptable}mm")
        
        # Find best fitting sizes
        best_length_score = 0
        all_size_scores = []  # Track all sizes with their scores
        
        for size_info in all_sizes:
            size_avg = size_info['avg_length']
            size_min = size_info['min_length']
            size_max = size_info['max_length']
            
            print(f"🔍 DEBUG: Evaluating size {size_info['size'].type} {size_info['size'].value} (avg: {size_avg}mm)")
            
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
                
                size_rec = {
                    'size_value': size_info['size'].value,
                    'size_type': size_info['size'].type,
                    'size_table': size_info['table'].name,
                    'fit_type': fit_type,
                    'fit_note': fit_note,
                    'score': length_score,
                    'insole_length': f"{size_info['min_length']}-{size_info['max_length']}mm",
                    'deviation': deviation
                }
                
                size_recommendations.append(size_rec)
                all_size_scores.append(length_score)
                
                print(f"✅ DEBUG: Size {size_info['size'].value} - {fit_type} (score: {length_score}, deviation: {deviation}mm)")
                
                best_length_score = max(best_length_score, length_score)
            else:
                # Size is outside acceptable range, but still track for fallback
                if size_avg < min_acceptable:
                    diff = min_acceptable - size_avg
                    if diff <= 5:
                        length_score = 0.5
                        fit_type = "too small but wearable"
                    elif diff <= 10:
                        length_score = 0.3
                        fit_type = "too small"
                    else:
                        length_score = 0.0
                        fit_type = "much too small"
                else:  # size_avg > max_acceptable
                    diff = size_avg - max_acceptable
                    if diff <= 5:
                        length_score = 0.6
                        fit_type = "slightly large"
                    elif diff <= 10:
                        length_score = 0.4
                        fit_type = "too large"
                    else:
                        length_score = 0.0
                        fit_type = "much too large"
                
                all_size_scores.append(length_score)
                print(f"⚠️ DEBUG: Size {size_info['size'].value} - {fit_type} (score: {length_score})")
        
        print(f"🔍 DEBUG: Found {len(size_recommendations)} recommended sizes")
        
        # If no perfect matches, add the closest sizes as recommendations
        if not size_recommendations and all_sizes:
            print("⚠️ DEBUG: No perfect sizes found, looking for closest alternatives...")
            
            # Find the 3 closest sizes
            sizes_with_distance = []
            for size_info in all_sizes:
                distance = abs(size_info['avg_length'] - ideal_insole)
                sizes_with_distance.append({
                    'size_info': size_info,
                    'distance': distance
                })
            
            # Sort by distance and take top 3
            sizes_with_distance.sort(key=lambda x: x['distance'])
            
            for item in sizes_with_distance[:3]:
                size_info = item['size_info']
                distance = item['distance']
                
                # Calculate a score based on distance
                if distance <= 5:
                    length_score = 0.6
                    fit_type = "close fit"
                elif distance <= 10:
                    length_score = 0.4
                    fit_type = "workable"
                elif distance <= 15:
                    length_score = 0.3
                    fit_type = "not ideal"
                else:
                    length_score = 0.2
                    fit_type = "poor fit"
                
                # Determine if too small or too large
                if size_info['avg_length'] < ideal_insole:
                    fit_note = "runs small"
                else:
                    fit_note = "runs large"
                
                size_recommendations.append({
                    'size_value': size_info['size'].value,
                    'size_type': size_info['size'].type,
                    'size_table': size_info['table'].name,
                    'fit_type': fit_type,
                    'fit_note': fit_note,
                    'score': length_score,
                    'insole_length': f"{size_info['min_length']}-{size_info['max_length']}mm",
                    'deviation': distance
                })
                
                best_length_score = max(best_length_score, length_score)
                print(f"📌 DEBUG: Added alternative size {size_info['size'].value} (distance: {distance}mm)")
        
        # Calculate the final length score component
        score_components['length'] = best_length_score * 40
        print(f"🔍 DEBUG: Length score: {score_components['length']:.1f}/40")
        
        # --- 2. WIDTH MATCHING (35% weight) ---
        foot_width_category = scan.width_category()
        product_width = self.width
        
        print(f"🔍 DEBUG: Foot width category: {foot_width_category}, Product width: {product_width}")
        
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
        print(f"🔍 DEBUG: Width score: {score_components['width']:.1f}/35")
        
        # --- 3. TOE BOX MATCHING (15% weight) ---
        foot_toe_box = scan.toe_box_category()
        product_toe_box = self.toe_box
        
        print(f"🔍 DEBUG: Foot toe box: {foot_toe_box}, Product toe box: {product_toe_box}")
        
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
        print(f"🔍 DEBUG: Toe box score: {score_components['toe_box']:.1f}/15")
        
        # --- 4. GENDER MATCHING (10% weight) ---
        # This is a soft match - doesn't disqualify but affects score
        user_gender = getattr(scan.user, 'gender', None)
        
        print(f"🔍 DEBUG: User gender: {user_gender}, Product gender: {self.gender}")
        
        if user_gender and user_gender.lower() == self.gender.lower():
            gender_score = 1.0
        else:
            gender_score = 0.5  # Still acceptable, just noted
        
        score_components['gender'] = gender_score * 10
        print(f"🔍 DEBUG: Gender score: {score_components['gender']:.1f}/10")
        
        # --- CALCULATE TOTAL SCORE ---
        total_score = sum(score_components.values())
        print(f"🔍 DEBUG: Total score: {total_score:.1f}/100")
        
        # Sort size recommendations by score, then by deviation
        size_recommendations.sort(key=lambda x: (-x['score'], x.get('deviation', 999)))
        
        # Limit to top 3 recommendations
        size_recommendations = size_recommendations[:3]
        
        # Remove deviation from final output (was just for sorting)
        for rec in size_recommendations:
            rec.pop('deviation', None)
        
        print(f"✅ DEBUG: Final recommendations: {len(size_recommendations)}")
        
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

class Quantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quantities')
    size = models.ForeignKey('SizeTable', on_delete=models.CASCADE, related_name='size_quantities')
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.quantity})"

    class Meta:
        unique_together = ('product', 'size'),
        verbose_name = "Size & Quantity"
        verbose_name_plural = "Sizes & Quantity"

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
    