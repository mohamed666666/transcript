from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class MemberManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "date_of_birth"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Add related_name for user_permissions and groups
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='members',
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='members',
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    
    
class Transcription(models.Model):
    user = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='transcriptions',
    )
    transcription_text = models.TextField()
    transcription_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcription by {self.user} on {self.transcription_date}"