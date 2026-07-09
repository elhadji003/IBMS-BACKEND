from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)  # Fondations, Bureautique, Marketing
    image_url = models.URLField(blank=True, null=True)
    is_foundational = models.BooleanField(default=False)  # True uniquement pour "Maîtriser son ordinateur"
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    @property
    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title


class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="user_progress")
    progress_percentage = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    # Précision importante : started_at doit être fixé dès la création de l'instance
    started_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def save(self, *args, **kwargs):
        # Sécurité F5 : Si l'étudiant commence, on fige définitivement la date de départ
        if not self.started_at:
            self.started_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} - {self.course.title}"

    @property
    def time_remaining(self):
        """
        Temps restant avant déblocage du quiz (en secondes).
        """
        if self.is_completed:
            return 0

        if not self.started_at:
            return 120

        unlock_time = self.started_at + timedelta(seconds=120)
        remaining = (unlock_time - timezone.now()).total_seconds()

        return max(0, int(remaining))

    @property
    def is_quiz_unlocked(self):
        """
        Le quiz est disponible uniquement après les 120 secondes.
        """
        return self.time_remaining == 0