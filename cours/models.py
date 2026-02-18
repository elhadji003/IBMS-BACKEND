from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    parteners_name = models.CharField(max_length=255)
    parteners_number = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=0)  # 0 = gratuit
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_free(self):
        return self.price == 0

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="contents")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="courses/files/", null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    order = models.IntegerField(default=0)


class CoursePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    amount = models.IntegerField()
    payment_method = models.CharField(max_length=50)  # wave
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid")],
        default="pending"
    )

    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
