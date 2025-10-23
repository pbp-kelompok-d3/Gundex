from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):

    bio = models.TextField(max_length=500, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username}'s Profile"