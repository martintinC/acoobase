from django import forms
from .models import Sortie, Incident, Rameur

class SortieForm(forms.ModelForm):
    barreur = forms.ModelChoiceField(
        queryset=Rameur.objects.filter(actif=True),
        required=False,
        label="Barreur",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Sortie
        fields = ["bateau", "barreur"]
        widgets = {
            "bateau": forms.Select(attrs={"class": "form-control", "id": "selectBateau"}),
        }

class IncidentForm(forms.ModelForm):
    bateau_immobilise = forms.BooleanField(
        required=False,
        label="Immobiliser le bateau"
    )

    class Meta:
        model = Incident
        exclude = ['commentaire', 'date_cloture']