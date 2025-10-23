from django import forms
from .models import LogPendakian
from explore_gunung.models import Gunung

class DateInput(forms.DateInput):
    input_type = "date"

class LogPendakianForm(forms.ModelForm):
    gunung = forms.ModelChoiceField(queryset=Gunung.objects.none(), label="Gunung")

    class Meta:
        model = LogPendakian
        fields = ["gunung", "start_date", "end_date", 
                  "notes", "summit_reached", "team_size", 
                  "rating"
                ]
        
        widgets = {
            "start_date": DateInput(attrs={"class": "lp-input"}),
            "end_date": DateInput(attrs={"class": "lp-input"}),
            "team_size": forms.NumberInput(attrs={"min": 1, "class": "lp-input"}),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "lp-input"}),
            "notes": forms.Textarea(attrs={"rows": 5, "class": "lp-textarea", "placeholder": "Tulis catatan pendakian…"}),
        }

        labels = {
            "start_date": "Mulai",
            "end_date": "Selesai",
            "notes": "Catatan",
            "summit_reached": "Sampai Puncak",
            "team_size": "Ukuran Tim (opsional)",
            "rating": "Rating (1–5, opsional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Gunung.objects.all().order_by("nama")
        self.fields["gunung"].queryset = qs
        self.fields["gunung"].empty_label = "----------"
        self.fields["gunung"].label_from_instance = lambda obj: getattr(obj, "nama", str(obj))
        self.fields["team_size"].required = False
        self.fields["rating"].required = False
