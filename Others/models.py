from Products.models import PartnerProduct
from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
from Products.models import Product
from datetime import datetime
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
    slug = models.CharField(max_length=255, blank=True, null=True, help_text="English slug for the answer")

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
    left_length = models.DecimalField(max_digits=10, decimal_places=2, help_text="Left foot length in mm")
    right_length = models.DecimalField(max_digits=10, decimal_places=2, help_text="Right foot length in mm")

    # Foot width (mm)
    left_width = models.DecimalField(max_digits=10, decimal_places=2, help_text="Left foot width in mm")
    right_width = models.DecimalField(max_digits=10, decimal_places=2, help_text="Right foot width in mm")

    # Arch Index (for future insole recommendation)
    left_arch_index = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    right_arch_index = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Heel Angle
    left_heel_angle = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                          help_text="Left heel angle in degrees")
    right_heel_angle = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                           help_text="Right heel angle in degrees")
    
    def save(self, *args, **kwargs):
        for field in ['left_length', 'right_length', 'left_width', 'right_width', 
                     'left_arch_index', 'right_arch_index', 'left_heel_angle', 'right_heel_angle']:
            val = getattr(self, field)
            if val is not None:
                try:
                    setattr(self, field, round(val, 2))
                except TypeError:
                    pass
        super().save(*args, **kwargs)

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

class Order(models.Model):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("packaging", "Packaging"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    )
    order_id = models.CharField(max_length=100, verbose_name="Order ID",blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partner_orders", null=True, blank=True, help_text="Partner who fulfilled this order")
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Price at time of purchase")
    quantity = models.IntegerField(default=1)
    size = models.ForeignKey(PartnerProductSize, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    color = models.CharField(max_length=10)
    status = models.CharField(max_length=10, default="pending", choices=ORDER_STATUS)
    tracking = models.CharField(max_length=100, verbose_name="Tracking ID",blank=True,null=True)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Net amount after fees and charges")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Created at (UTC)")
    
    def save(self, *args, **kwargs):
        if self.price is not None:
            try:
                self.price = round(self.price, 2)
            except TypeError:
                pass
        if self.net_amount is not None:
            try:
                self.net_amount = round(self.net_amount, 2)
            except TypeError:
                pass
            
        if not self.id:
            super().save(*args, **kwargs)
        
        if not self.order_id:
            self.order_id = f"ORD-{datetime.now().year}-{self.id:03d}"
            super().save(update_fields=['order_id'])
        if not self.tracking:
            self.tracking = f"DE{random.randint(1000000000, 9999999999)}"
            super().save(update_fields=['tracking'])
        else:
            super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.order_id}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_from = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_to = models.ForeignKey(User, on_delete=models.CASCADE,related_name="payments")
    product = models.ForeignKey(PartnerProduct, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transaction_id = models.CharField(max_length=100, verbose_name="Transaction ID",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.amount is not None:
            try:
                self.amount = round(self.amount, 2)
            except TypeError:
                pass
        if self.net_amount is not None:
            try:
                self.net_amount = round(self.net_amount, 2)
            except TypeError:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id}"

class Warehouse(models.Model):
    partner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    product = models.ManyToManyField(PartnerProduct,related_name="warehouse",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Finance(models.Model):
    partner = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField(default=2024)
    month = models.IntegerField(default=1)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    this_month_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    next_payout = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_payout = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reserved_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        for field in ['balance', 'this_month_revenue', 'next_payout', 'last_payout', 'reserved_amount']:
            val = getattr(self, field)
            if val is not None:
                try:
                    setattr(self, field, round(val, 2))
                except TypeError:
                    pass
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('partner', 'year', 'month')
        verbose_name = "Finance Record"
        verbose_name_plural = "Finance Records"

    def __str__(self):
        return f"{self.partner.email} - {self.year}/{self.month:02d} - Balance: {self.balance} Revenue: {self.this_month_revenue} "

class OrderInvoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="invoice_user")
    partner = models.ForeignKey(User, on_delete=models.CASCADE,related_name="invoice_partner")
    orders = models.ManyToManyField(Order, related_name='invoices', help_text="Orders included in this invoice")
    payments = models.CharField(max_length=100, help_text="Payments transaction ID for this invoice")
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total invoice amount")
    invoice_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL to the invoice PDF or receipt")
    created_date = models.DateTimeField(auto_now_add=True, help_text="Invoice creation date")
    
    def save(self, *args, **kwargs):
        if self.amount is not None:
            self.amount = round(self.amount, 2)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Order Invoice"
        verbose_name_plural = "Order Invoices"
        ordering = ['-created_date']
    
    def __str__(self):
        return f"Invoice #{self.id}  - ${self.amount} - {self.created_date.strftime('%Y-%m-%d %H:%M:%S')}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    partner_product = models.ForeignKey(PartnerProduct, on_delete=models.CASCADE)
    size = models.ForeignKey(PartnerProductSize, on_delete=models.CASCADE) # The specific size with stock
    color = models.CharField(max_length=50) # Storing color name as per requirement
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'partner_product', 'size', 'color')

    @property
    def total_price(self):
        return self.quantity * self.partner_product.price

    def __str__(self):
        return f"{self.quantity} x {self.partner_product.product.name} ({self.size})"

class Accessories(models.Model):
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accessories')
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='accessories')
    description = models.TextField(blank=True, null=True)
    eanc = models.CharField(max_length=13, null=True, blank=True, help_text="EAN code for this accessory")
    price = models.DecimalField(max_digits=12, decimal_places=2,null=True,blank=True)
    stock = models.IntegerField(default=0)
    article = models.CharField(max_length=100, null=True, blank=True, help_text="Article number for this accessory")
    image = models.ImageField(upload_to='accessories/',storage=MediaCloudinaryStorage(),blank=False, null=False,help_text="Image size should be less than 1MB")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, related_name='accessories', null=True, blank=True)
    online = models.BooleanField(default=True)
    local = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

