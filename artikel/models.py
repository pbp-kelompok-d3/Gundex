from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class Artikel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    title = models.CharField(max_length=255, null=False) 
    description = models.TextField()
    image = models.URLField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)   # waktu artikel dibuat
    updated_at = models.DateTimeField(auto_now=True) 
    views = models.PositiveIntegerField(default=0) 

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_artikels", blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
    