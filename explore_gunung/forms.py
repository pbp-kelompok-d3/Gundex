from django.forms import ModelForm
from explore_gunung.models import Gunung
from django.utils.html import strip_tags

class GunungForm(ModelForm):
    class Meta:
        def clean_nama(self):
            nama = self.cleaned_data["nama"]
            return strip_tags(nama)

        def clean_deksripsi(self):
            deksripsi = self.cleaned_data["deksripsi"]
            return strip_tags(deksripsi)
        
        model = Gunung
        fields = ["nama", "ketinggian", "provinsi", "foto", "deksripsi"]