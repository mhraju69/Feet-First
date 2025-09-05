import random
from django.db import models
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

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
        ('partner', 'Partner'),
        ('admin', 'Admin'),
    )
    name = models.CharField(max_length=200, blank=True, null=True,verbose_name="User Name")
    email = models.EmailField(max_length=255,unique=True,verbose_name="User Email")
    role = models.CharField(max_length=10, choices=ROLE, default='customer',verbose_name="User Role")
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True,storage=MediaCloudinaryStorage())
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=[('german', 'German'),('italian', 'Italian'),],default='german',verbose_name="User Language")
    is_active = models.BooleanField(default=False,verbose_name="Active User")
    is_staff = models.BooleanField(default=False,verbose_name="Staff User")  
    is_superuser = models.BooleanField(default=False,verbose_name="Super User")  
    objects = UserManager()
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Joineing Date")
    last_login = models.DateTimeField(auto_now=True)
    suspend = models.BooleanField(default=False,verbose_name="Suspend User")
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

    def save(self, *args, **kwargs):
        if self.suspend:
            self.is_active = False
        super().save(*args, **kwargs)

class OTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='user_otp',  
        on_delete=models.CASCADE
    )
    otp = models.CharField(max_length=6,verbose_name="OTP Code")
    created_at = models.DateTimeField(auto_now_add=True)
    attempt_count = models.IntegerField(default=0)  
    last_tried = models.DateTimeField(null=True, blank=True)  

    def __str__(self):
        return f"OTP for: {self.user}."

    @staticmethod
    def generate_otp(user):
        otp_code = str(random.randint(1000, 9999))
        return OTP.objects.create(user=user, otp=otp_code)

    def is_expired(self):
        return self.created_at + timedelta(minutes=3) < timezone.now()

    def can_try(self):
        """Return True if user can try now"""
        if self.attempt_count < 3:
            return True
        if self.last_tried + timedelta(minutes=1) < timezone.now():
            # reset count after 1 min
            self.attempt_count = 0
            self.save()
            return True
        return False

    def record_attempt(self):
        """Update attempt_count and last_tried"""
        self.attempt_count += 1
        self.last_tried = timezone.now()
        self.save() 
  
class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="addresses"
    )
    street = models.CharField(max_length=255)
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

class AccountDeletionRequest(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="deletion_requests")
    reason = models.JSONField(default=list, blank=True) 
    confirmed = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now_add=True,verbose_name="Deletion Request Date")

    def __str__(self):
        return f"Deletion request by {self.user.email} - {self.reason}"
    
    def save(self, *args, **kwargs):
        if self.confirmed:
            self.user.delete()  
        super().save(*args, **kwargs)

