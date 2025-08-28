import json
from django.http import JsonResponse
from ..models import Rameur, Bateau, Sortie, SortieRameur

def liste_rameurs(request):
    rameurs = list(Rameur.objects.values('id', 'prenom', 'nom', 'date_naissance'))
    return JsonResponse({'rameurs': rameurs})

def liste_bateaux(request):
    bateaux = list(Bateau.objects.values('id', 'nom', 'nombre_rameurs'))
    return JsonResponse({'bateaux': bateaux})

def details_sortie(request, sortie_id):
    sortie = Sortie.objects.filter(id=sortie_id).values().first()
    if sortie:
        return JsonResponse({'sortie': sortie})
    return JsonResponse({'error': 'Sortie non trouvée'}, status=404)

def get_rameurs(request, bateau_id):
    try:
        bateau = Bateau.objects.get(id=bateau_id)
    except Bateau.DoesNotExist:
        return JsonResponse({"error": "Bateau non trouvé"}, status=404)
    rameurs_en_sortie = SortieRameur.objects.filter(sortie__fin__isnull=True).values_list("rameur_id", flat=True)
    rameurs_disponibles = Rameur.objects.exclude(id__in=rameurs_en_sortie)
    return JsonResponse({
        "nombre_rameurs": bateau.nombre_rameurs,
        "rameurs": list(rameurs_disponibles.values("id", "prenom", "nom"))
    })