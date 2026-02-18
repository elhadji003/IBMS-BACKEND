from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super-admin')
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
    @property
    def is_staff(self):
        # L'accès au dashboard Django dépend du rôle
        return self.role in [self.UserRole.ADMIN, self.UserRole.SUPER_ADMIN]

    # 🔑 Obligatoire pour JWT / Django auth
    def get_by_natural_key(self, email):
        return self.get(email=email)
