from django.db import models
from .cours import Course
from django.core.exceptions import ValidationError

class CourseContent(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="contents"
    )
    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="courses/files/",
        null=True,
        blank=True
    )
    video_url = models.URLField(null=True, blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def clean(self):
        if self.file and self.video_url:
            raise ValidationError(
                "Un contenu ne peut pas avoir un fichier ET une vidéo"
            )

    def __str__(self):
        return self.title
