from django.shortcuts import render
from ..models import Incident

def atelier(request):
    incidents_en_cours = Incident.objects.filter(date_cloture__isnull=True).order_by('-date_creation')
    incidents_clotures = Incident.objects.filter(date_cloture__isnull=False).order_by('-date_cloture')
    context = {
        "incidents_en_cours": incidents_en_cours,
        "incidents_clotures": incidents_clotures
    }
    return render(request, "cahierDeSorties/atelier.html", context)