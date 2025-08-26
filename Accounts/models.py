from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from multiselectfield import MultiSelectField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(verbose_name="email address",max_length=255,unique=True,)
    role = models.CharField(max_length=10, choices=ROLE, default='customer')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=[('german', 'German'),('italian', 'Italian'),],default='german')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    objects = UserManager()
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

class OTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='user_otp',  
        on_delete=models.CASCADE
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Your OTP is: {self.otp}. Please keep it secure and do not share it with anyone."

    @staticmethod
    def generate_otp(user):
        import random
        otp_code = ''.join(random.choices('0123456789', k=6))
        otp = OTP.objects.create(user=user, otp=otp_code)
        otp.save()
        return otp
  
class OnboardingSurvey(models.Model):

    # Foreign key to the user
    user =  models.OneToOneField(User, on_delete=models.CASCADE, related_name="survey")

    # Step 2: How did you hear about FeetFirst?
    SOURCE_CHOICES = [
        ("social_media", "Through social media (Instagram, Facebook, etc.)"),
        ("partner_store", "In a partner store"),
        ("scan_event", "During a scan event"),
        ("word_of_mouth", "By word of mouth (friend’s suggestion)"),
        ("other", "Other"),
    ]
    source = MultiSelectField(choices=SOURCE_CHOICES, max_length=200)  # 👈 multiple choices allowed

    # Step 3: Which products do you use the most?
    PRODUCT_CHOICES = [
        ("man", "Man"),
        ("woman", "Woman"),
    ]
    product_preference = models.CharField(max_length=10, choices=PRODUCT_CHOICES)

    # Step 4: Free text for foot/shoe problems
    foot_problems = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey of {self.user.email if self.user else 'Unknown User'}"

class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="addresses"
    )
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = [ "-created_at"]

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"
