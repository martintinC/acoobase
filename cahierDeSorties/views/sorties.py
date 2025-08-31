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
    bateaux_disponibles = Bateau.objects.exclude(id__in=bateaux_en_sortie).filter(immobile=False).order_by('nom')
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
        barreur_id = request.POST.get("barreur")

        try:
            bateau = Bateau.objects.get(id=bateau_id)
        except Bateau.DoesNotExist:
            return JsonResponse({"error": "Bateau non trouvé"}, status=404)

        barreur = None
        if barreur_id:
            try:
                barreur = Rameur.objects.get(id=barreur_id)
            except Rameur.DoesNotExist:
                return JsonResponse({"error": "Barreur non trouvé"}, status=404)

        sortie = Sortie.objects.create(
            bateau=bateau,
            debut=now(),
            distance=None,
            barreur=barreur if (bateau.barre and barreur) else None
        )

        # Associer les rameurs à la sortie via la table intermédiaire SortieRameur
        for rameur_id in rameurs_ids:
            if barreur and int(rameur_id) == barreur.id:
                continue  # Ne pas associer le barreur comme rameur
            try:
                rameur = Rameur.objects.get(id=rameur_id)
                SortieRameur.objects.create(sortie=sortie, rameur=rameur)
            except Rameur.DoesNotExist:
                return JsonResponse({"error": f"Rameur avec ID {rameur_id} non trouvé"}, status=404)

        return JsonResponse({"success": True})

    # GET : filtrer les bateaux non immobilisés et non en sortie
    sorties = Sortie.objects.filter(fin__isnull=True)
    bateaux_en_sortie = sorties.values_list("bateau_id", flat=True)
    bateaux_disponibles = Bateau.objects.exclude(id__in=bateaux_en_sortie).filter(immobile=False)
    form = SortieForm()
    form.fields["bateau"].queryset = bateaux_disponibles
    return render(request, "cahierDeSorties/sorties_en_cours.html", {"form": form})

def supprimer_sortie(request, sortie_id):
    if request.method == "POST":
        sortie = get_object_or_404(Sortie, id=sortie_id)
        bateau = sortie.bateau
        sortie.delete()
        bateau.en_sortie = False
        bateau.save()
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
            sortie.bateau.en_sortie = False
            sortie.bateau.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})