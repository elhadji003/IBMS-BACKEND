from django.db import models
from django.conf import settings
from .courses import Course

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course.title} - {self.text[:30]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # Une seule bonne réponse

    def __str__(self):
        return self.text

class QuizSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.IntegerField()  # Pourcentage de bonnes réponses (ex: 80)
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)