from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class OnboardingSurvey(models.Model):

    # Foreign key to the user
    user =  models.OneToOneField(User, on_delete=models.CASCADE, related_name="survey")

    sources = models.JSONField(default=list, blank=True)  # 👈 multiple choices allowed

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
        return f"Survey of {self.user.email}"
