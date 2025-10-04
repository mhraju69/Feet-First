from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.


class Ques(models.Model):  # Parent = holds sub_category
    title = models.CharField(max_length=100, verbose_name="Question_title")
    created_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    def __str__(self):
        return self.title

class Ans(models.Model):  # Child = belongs to a Questions record
    answer = models.CharField(max_length=100)
    parent = models.ForeignKey(
        Ques,
        on_delete=models.CASCADE,
        related_name='ans_list',verbose_name="Related Question"
    )

    class Meta:
        verbose_name = 'Answer'
    

    def __str__(self):
        return f"Answer: {self.answer} for Question: {self.parent.title}"
    
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
    image = models.ImageField(upload_to='news_images/',storage=MediaCloudinaryStorage())
    content_de = models.TextField(verbose_name ="Content (German)")
    content_it = models.TextField(verbose_name="Content (Italian)")
    created_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return f"{self.title_de} - {self.title_it}"
