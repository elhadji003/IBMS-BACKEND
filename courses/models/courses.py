from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)  # Fondations, Bureautique, Marketing
    image_url = models.URLField(blank=True, null=True)
    is_foundational = models.BooleanField(default=False)  # True uniquement pour "Maîtriser son ordinateur"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="user_progress")
    progress_percentage = models.IntegerField(default=0)  # De 0 à 100
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')  # Un utilisateur ne peut avoir qu'un seul suivi par cours

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress_percentage}%)"