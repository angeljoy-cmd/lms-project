from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = 'Users'
