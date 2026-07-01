from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

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
    
    # --- NOUVEAU CHAMP ---
    # Enregistre le moment exact où la ligne est créée (première visite du cours)
    started_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress_percentage}%)"

    # --- PROPRIÉTÉS DYNAMIQUES POUR TON API ---

    @property
    def time_remaining(self):
        """Calcule le nombre de secondes restantes avant d'atteindre 1 heure."""
        if self.is_completed or self.progress_percentage == 100:
            return 0
            
        unlocked_time = self.started_at + timedelta(seconds=120)
        now = timezone.now()
        
        if now >= unlocked_time:
            return 0
            
        return int((unlocked_time - now).total_seconds())

    @property
    def is_quiz_unlocked(self):
        """Renvoie True si l'heure est passée ou si le cours est déjà complété."""
        return self.time_remaining == 0