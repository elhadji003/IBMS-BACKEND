from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .manage import UserManager
from django.core.validators import RegexValidator


phone_regex = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Le numéro doit être au format international. Ex: +221771234567"
)

class User(AbstractBaseUser, PermissionsMixin):

    class UserRole:
        USER = "user"
        ADMIN = "admin"
        SUPER_ADMIN = "super-admin"

        CHOICES = [
            (USER, "Utilisateur"),
            (ADMIN, "Admin"),
            (SUPER_ADMIN, "Super Admin"),
        ]

    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.USER
    )

    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(unique=True, db_index=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        unique=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return self.role in ["admin", "super-admin"]

    @property
    def is_admin(self):
        return self.role in ["admin", "super-admin"]

    @property
    def is_super_admin(self):
        return self.role == "super-admin"
