from django import forms
from .models import Sortie, Incident

class SortieForm(forms.ModelForm):
    class Meta:
        model = Sortie
        fields = ["bateau"]  # Seul le bateau est sélectionnable au départ
        widgets = {
            "bateau": forms.Select(attrs={"class": "form-control", "id": "selectBateau"}),  # Sélecteur de bateau
        }

        
class IncidentForm(forms.ModelForm):
    bateau_immobilise = forms.BooleanField(
        required=False,
        label="Immobiliser le bateau"
    )

    class Meta:
        model = Incident
        exclude = ['commentaire', 'date_cloture']