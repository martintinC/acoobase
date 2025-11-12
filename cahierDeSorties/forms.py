from django import forms
from .models import Bateau, Sortie, Incident, Rameur

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
    createur = forms.ModelChoiceField(
        queryset=Rameur.objects.filter(actif=True).order_by('prenom', 'nom'),
        label="Créateur",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    bateau = forms.ModelChoiceField(
        queryset=Bateau.objects.all().order_by('nom'),
        required=False,
        label="Bateau",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    bateau_immobilise = forms.BooleanField(
        required=False,
        label="Immobiliser le bateau"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        required=False
    )

    class Meta:
        model = Incident
        exclude = ['commentaire', 'date_cloture']