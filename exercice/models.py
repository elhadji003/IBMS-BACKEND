from django.db import models
from django.contrib.auth import settings
from courses.models import Course 

class ExerciseModule(models.Model):
    """
    Regroupe les exercices par module de cours (ex: Microsoft Excel, Word...)
    """
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='exercise_module', verbose_name="Cours associé")
    title = models.CharField(max_length=200, verbose_name="Titre du module d'exercices")
    icon = models.CharField(max_length=10, default="💻", help_text="Emoji représentatif")

    def __str__(self):
        return f"Exercices de : {self.course.title}"


class Exercise(models.Model):
    """
    Un exercice spécifique appartenant à un module.
    """
    DIFFICULTY_CHOICES = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
    ]

    module = models.ForeignKey(ExerciseModule, on_delete=models.CASCADE, related_name='exercises')
    exercise_id = models.IntegerField(help_text="Numéro de l'exercice au sein du module (ex: 1, 2, 3)")
    title = models.CharField(max_length=200)
    desc = models.TextField(verbose_name="Description / Consigne")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Débutant')

    class Meta:
        ordering = ['exercise_id']
        unique_together = ('module', 'exercise_id')

    def __str__(self):
        return f"{self.module.title} - Ex {self.exercise_id} : {self.title}"


class ExerciseSubmission(models.Model):
    """
    Suit l'état d'avancement et la validation par l'admin pour chaque étudiant.
    """
    STATUS_CHOICES = [
        ('not_started', 'Non lancé'),
        ('in_progress', 'En cours'),
        ('pending', 'En attente de validation'),
        ('validated', 'Validé par l\'Admin'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exercise_submissions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    submitted_at = models.DateTimeField(auto_now=True)
    admin_feedback = models.TextField(blank=True, null=True, verbose_name="Commentaire de l'enseignant")

    class Meta:
        unique_together = ('student', 'exercise')

    def __str__(self):
        return f"{self.student.first_name} - {self.exercise.title} ({self.get_status_display()})"