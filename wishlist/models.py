from django.db import models
from userprofile.models import UserProfile
from explore_gunung.models import Gunung 

class WishlistItem(models.Model):
    # Menghubungkan ke pengguna yang login
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # Menghubungkan ke gunung yang dipilih
    gunung = models.ForeignKey(Gunung, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Memastikan 1 user tidak bisa menambahkan gunung yang sama 2x
        unique_together = ('user', 'gunung')

    def __str__(self):
        return f"{self.user.username} - {self.gunung.nama}" # Asumsi model Gunung punya atribut 'nama'