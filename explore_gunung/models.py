import uuid
from django.db import models

class Gunung(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255)
    ketinggian = models.PositiveIntegerField(default=0)
    provinsi = models.CharField(max_length=255)
    foto = models.URLField(blank=True, null=True)
    deksripsi = models.TextField()
    
    def __str__(self):
        return self.nama
