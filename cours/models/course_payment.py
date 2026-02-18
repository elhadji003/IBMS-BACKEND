import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

from .cours import Course

class CoursePayment(models.Model):
    # Génère une référence unique type 'PAY-12345' pour TouchPay
    transaction_ref = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'En attente'), ('paid', 'Payé'), ('failed', 'Echoué')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)