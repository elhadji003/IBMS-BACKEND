from django.db import models
from cours.models import Course
from django.core.exceptions import ValidationError

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="contents")
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    # Les 3 options possibles
    file = models.FileField(upload_to="courses/docs/", null=True, blank=True)
    video_file = models.FileField(upload_to="courses/videos/", null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def clean(self):
        # On compte combien de champs sont remplis
        contents = [self.file, self.video_file, self.video_url]
        filled_count = len([c for c in contents if c])

        if filled_count > 1:
            raise ValidationError("Choisissez UN SEUL type : soit un fichier, soit une vidéo locale, soit un lien YouTube.")
        if filled_count == 0:
            raise ValidationError("Vous devez ajouter au moins un contenu (Fichier, Vidéo ou URL).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)