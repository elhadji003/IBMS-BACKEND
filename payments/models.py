from django.db import models
from django.conf import settings
from courses.models import Course

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        PAID = "PAID", "Payé"
        FAILED = "FAILED", "Échoué"
        CANCELED = "CANCELED", "Annulé"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="XOF")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Reste bien sur ce nom exact :
    paydunya_invoice_token = models.CharField(max_length=255, blank=True, null=True, unique=True)
    paydunya_url = models.URLField(blank=True, null=True)
    external_transaction_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} - {self.status}"