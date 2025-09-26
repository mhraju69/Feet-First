from django.db import models

# Create your models here.
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

class Questions(models.Model):  # Parent = holds sub_category
    sub_category = models.CharField(max_length=100,choices=SubCategory, unique=True)
    Question = models.CharField(max_length=100)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.Question or "No SubCategory"
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'   

class Ans(models.Model):  # Child = belongs to a Questions record
    answer = models.CharField(max_length=100)
    parent = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        related_name='ans_list'
    )

    class Meta:
        verbose_name = 'Answer'
    

    def __str__(self):
        return f"Answer: {self.answer}"
    