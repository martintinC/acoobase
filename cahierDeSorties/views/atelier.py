from django.shortcuts import render, redirect, get_object_or_404
from ..models import Incident
from ..forms import IncidentForm
from django.utils import timezone
from django.views.decorators.http import require_POST

def atelier(request):
    incidents_en_cours = Incident.objects.filter(date_cloture__isnull=True).order_by('-date_creation')
    incidents_clotures = Incident.objects.filter(date_cloture__isnull=False).order_by('-date_cloture')
    context = {
        "incidents_en_cours": incidents_en_cours,
        "incidents_clotures": incidents_clotures
    }
    return render(request, "cahierDeSorties/atelier.html", context)


def creer_incident(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            # Met à jour le champ immobile du bateau si la case est cochée
            if form.cleaned_data.get('bateau_immobilise'):
                incident.bateau.immobile = True
                incident.bateau.save()
            return redirect('atelier')
    else:
        form = IncidentForm()
    return render(request, "cahierDeSorties/creer_incident.html", {"form": form})


@require_POST
def cloturer_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    incident.date_cloture = timezone.now()
    incident.save()
    bateau = incident.bateau
    # Vérifie s'il reste des incidents en cours pour ce bateau
    incidents_en_cours = Incident.objects.filter(bateau=bateau, date_cloture__isnull=True).exclude(id=incident.id)
    if not incidents_en_cours.exists():
        bateau.immobile = False
        bateau.save()
    return redirect('atelier')

@require_POST
def editer_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    commentaire = request.POST.get("commentaire", "")
    immobile = request.POST.get("immobile") == "1"
    # Met à jour le commentaire
    incident.commentaire = commentaire
    incident.save()
    # Met à jour le champ immobile du bateau lié
    bateau = incident.bateau
    bateau.immobile = immobile
    bateau.save()
    return redirect('atelier')