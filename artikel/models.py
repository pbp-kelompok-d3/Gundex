from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
class Artikel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    title = models.CharField(max_length=255, null=False) 
    description = models.TextField()
    image = models.URLField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)   # waktu artikel dibuat
    updated_at = models.DateTimeField(auto_now=True) 
    views = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.title
    