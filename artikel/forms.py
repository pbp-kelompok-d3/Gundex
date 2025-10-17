from django.forms import ModelForm
from artikel.models import Artikel

class ArtikelForm(ModelForm):
    class Meta:
        model = Artikel
        fields = ['title', 'description', 'image']