from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import datetime
from ..models import Bateau, Sortie, Rameur, SortieRameur
from ..forms import SortieForm

def sorties_en_cours(request):
    today = datetime.now().date()
    sorties = Sortie.objects.filter(fin__isnull=True)
    bateaux_en_sortie = sorties.values_list("bateau_id", flat=True)
    bateaux_disponibles = Bateau.objects.exclude(id__in=bateaux_en_sortie)
    form = SortieForm()
    form.fields["bateau"].queryset = bateaux_disponibles
    return render(request, "cahierDeSorties/sorties_en_cours.html", {
        "sorties": sorties,
        "today": today,
        "form": form
    })

def ajouter_sortie(request):
    if request.method == "POST":
        bateau_id = request.POST.get("bateau")
        rameurs_ids = request.POST.getlist("rameurs[]")
        try:
            bateau = Bateau.objects.get(id=bateau_id)
        except Bateau.DoesNotExist:
            return JsonResponse({"error": "Bateau non trouvé"}, status=404)
        sortie = Sortie.objects.create(bateau=bateau, debut=now(), distance=None)
        for rameur_id in rameurs_ids:
            try:
                rameur = Rameur.objects.get(id=rameur_id)
                SortieRameur.objects.create(sortie=sortie, rameur=rameur)
            except Rameur.DoesNotExist:
                return JsonResponse({"error": f"Rameur avec ID {rameur_id} non trouvé"}, status=404)
        return JsonResponse({"success": True})
    form = SortieForm()
    return render(request, "cahierDeSorties/sorties_en_cours.html", {"form": form})

def supprimer_sortie(request, sortie_id):
    if request.method == "POST":
        sortie = get_object_or_404(Sortie, id=sortie_id)
        sortie.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

def valider_sortie(request, sortie_id):
    sortie = get_object_or_404(Sortie, id=sortie_id)
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            distance = data.get('kilometres')
            fin = data.get('fin')
            if fin:
                fin = datetime.now().replace(hour=int(fin.split(":")[0]), minute=int(fin.split(":")[1]), second=0, microsecond=0)
            if distance:
                sortie.distance = distance
            if fin:
                sortie.fin = fin
            sortie.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})