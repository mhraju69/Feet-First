from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
from Products.models import Product
from itertools import chain
from Products.models import *

class FAQ(models.Model):
    question_de = models.CharField(max_length=200 , verbose_name ="Question (German)")
    question_it = models.CharField(max_length=200 , verbose_name="Question (Italian)")
    answer_de = models.TextField(verbose_name ="Answer (German)")
    answer_it = models.TextField(verbose_name="Answer (Italian)")

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return f"FAQ for: {self.question_de}"

class News(models.Model):
    title_de = models.CharField(max_length=200 , verbose_name ="Title (German)")
    title_it = models.CharField(max_length=200 , verbose_name="Title (Italian)")
    image = models.ImageField(upload_to='news_images/',storage=MediaCloudinaryStorage(),help_text="Image size should be less than 1MB")
    content_de = models.TextField(verbose_name ="Content (German)")
    content_it = models.TextField(verbose_name="Content (Italian)")
    created_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return f"{self.title_de} - {self.title_it}"

class Question(models.Model):
    key = models.CharField(max_length=255, unique=True)
    label = models.TextField()

    def __str__(self):
        return self.label

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers", null=True, blank=True)
    key = models.CharField(max_length=255)
    label = models.TextField()

    def __str__(self):
        return f"{self.label}"
    
    @property
    def sub_category(self):
        return self.product.sub_category if self.product else None

    class Meta:
        verbose_name = 'Answer'

class ProductQuestionAnswer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="question_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="product_questions")
    answers = models.ManyToManyField(Answer,related_name="product_answers")

    def __str__(self):
        return f"{self.product.name} - {self.question.label}"
    class Meta:
        verbose_name = 'Question & Answer'

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
