from django import forms
from .models import Sortie

class SortieForm(forms.ModelForm):
    class Meta:
        model = Sortie
        fields = ["bateau"]  # Seul le bateau est sélectionnable au départ
        widgets = {
            "bateau": forms.Select(attrs={"class": "form-control", "id": "selectBateau"}),  # Sélecteur de bateau
        }
