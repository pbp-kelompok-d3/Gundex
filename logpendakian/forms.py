from django import forms
from .models import LogPendakian

class DateInput(forms.DateInput):
    input_type = "date"

class LogPendakianForm(forms.ModelForm):
    class Meta:
        model = LogPendakian
        fields = [
            "mountain_name", "start_date", "end_date",
            "notes", "summit_reached", "team_size", "rating",
        ]
        widgets = {
            "start_date": DateInput(),
            "end_date": DateInput(),
            "team_size": forms.NumberInput(attrs={"min": 1}),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }
        labels = {
            "mountain_name": "Nama Gunung",
            "start_date": "Mulai",
            "end_date": "Selesai",
            "notes": "Catatan",
            "summit_reached": "Sampai Puncak?",
            "team_size": "Ukuran Tim (opsional)",
            "rating": "Rating (1–5, opsional)",
        }

    def clean(self):
        cleaned = super().clean()
        s, e = cleaned.get("start_date"), cleaned.get("end_date")
        if s and e and e < s:
            self.add_error("end_date", "Tanggal selesai tidak boleh sebelum tanggal mulai.")
        return cleaned
