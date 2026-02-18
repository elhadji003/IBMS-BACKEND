from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Partner(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)  # 0 = gratuit
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_free(self):
        return self.price == 0

    def __str__(self):
        return self.title
