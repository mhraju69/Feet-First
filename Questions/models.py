from django.db import models
from Products.models import *
# Create your models here.

class Questions(models.Model):  # Parent = holds sub_category
    sub_category = models.CharField(max_length=100,choices=SubCategory, unique=True)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.sub_category or "No SubCategory"

class Ques(models.Model):  # Child = belongs to a Questions record
    questions = models.CharField(max_length=100)
    parent = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        related_name='ques_list'
    )

    class Meta:
        verbose_name = 'Add Question'
    

    def __str__(self):
        return f"Question: {self.questions}"
    
class Answer(models.Model):  # Parent = User submission
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answers by {self.user.name} at {self.created_at}"

class AnswerItem(models.Model):  # Child = Question + Answer
    parent = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='items')
    question = models.ForeignKey('Ques', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.question.questions} -> {self.answer_text}"