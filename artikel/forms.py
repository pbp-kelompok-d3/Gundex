from django.forms import ModelForm
from artikel.models import Artikel
from django.utils.html import strip_tags

class ArtikelForm(ModelForm):
    class Meta:
        model = Artikel
        fields = ['title', 'description', 'image']

    def clean_title(self):
        title = self.cleaned_data["title"]
        return strip_tags(title)

    def clean_description(self):
        description = self.cleaned_data["description"]
        return strip_tags(description)
