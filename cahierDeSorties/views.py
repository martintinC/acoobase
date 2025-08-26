import json
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.http import Http404
from .models import Incident, Rameur, Bateau, Sortie, SortieRameur  # Importation des modèles
from .forms import SortieForm  # Importation du formulaire
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, date
from django.db.models import Count, Sum
from .services.statistiques import kilometres_par_type_bateau
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Sortie
import calendar

# =========================================================================================
# API : Récupération des données
# =========================================================================================
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

# =========================================================================================
# Page des sorties en cours
# =========================================================================================
def sorties_en_cours(request):
    today = datetime.now().date()

    # Récupérer les sorties en cours (sans date de fin)
    sorties = Sortie.objects.filter(fin__isnull=True)

    # Exclure les bateaux qui sont déjà en sortie
    bateaux_en_sortie = sorties.values_list("bateau_id", flat=True)
    bateaux_disponibles = Bateau.objects.exclude(id__in=bateaux_en_sortie)

    # Formulaire d'ajout avec uniquement les bateaux disponibles
    form = SortieForm()
    form.fields["bateau"].queryset = bateaux_disponibles

    return render(request, "cahierDeSorties/sorties_en_cours.html", {
        "sorties": sorties,
        "today": today,
        "form": form
    })

# =========================================================================================
# Ajout d'une sortie
# =========================================================================================
def ajouter_sortie(request):
    if request.method == "POST":
        bateau_id = request.POST.get("bateau")
        rameurs_ids = request.POST.getlist("rameurs[]")  # Liste des rameurs sélectionnés

        try:
            bateau = Bateau.objects.get(id=bateau_id)  # Vérification du bateau
        except Bateau.DoesNotExist:
            return JsonResponse({"error": "Bateau non trouvé"}, status=404)

        sortie = Sortie.objects.create(bateau=bateau, debut=now(), distance=None)  # Création de la sortie

        # Associer les rameurs à la sortie via la table intermédiaire Sortie_rameur
        for rameur_id in rameurs_ids:
            try:
                rameur = Rameur.objects.get(id=rameur_id)
                SortieRameur.objects.create(sortie=sortie, rameur=rameur)  # Ajout du rameur à la sortie
            except Rameur.DoesNotExist:
                return JsonResponse({"error": f"Rameur avec ID {rameur_id} non trouvé"}, status=404)

        return JsonResponse({"success": True})

    form = SortieForm()
    return render(request, "cahierDeSorties/sorties_en_cours.html", {"form": form})

# =========================================================================================
# Suppression d'une sortie
# =========================================================================================
def supprimer_sortie(request, sortie_id):
    if request.method == "POST":
        sortie = get_object_or_404(Sortie, id=sortie_id)
        sortie.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


# =========================================================================================
# Validation d'une sortie
# =========================================================================================
def valider_sortie(request, sortie_id):
    sortie = get_object_or_404(Sortie, id=sortie_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            distance = data.get('kilometres')  # Distance en km
            fin = data.get('fin')  # Heure de fin de la sortie (au format HH:mm)

            # Convertir fin en datetime
            if fin:
                fin = datetime.now().replace(hour=int(fin.split(":")[0]), minute=int(fin.split(":")[1]), second=0, microsecond=0)

            # Enregistrement des données
            if distance:
                sortie.distance = distance
            if fin:
                sortie.fin = fin

            sortie.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

# =========================================================================================
# Récupération des rameurs en fonction du bateau sélectionné
# =========================================================================================
def get_rameurs(request, bateau_id):
    try:
        bateau = Bateau.objects.get(id=bateau_id)
    except Bateau.DoesNotExist:
        return JsonResponse({"error": "Bateau non trouvé"}, status=404)

    # Récupérer les rameurs qui sont en sortie actuellement
    rameurs_en_sortie = SortieRameur.objects.filter(sortie__fin__isnull=True).values_list("rameur_id", flat=True)

    # Exclure ces rameurs
    rameurs_disponibles = Rameur.objects.exclude(id__in=rameurs_en_sortie)

    return JsonResponse({
        "nombre_rameurs": bateau.nombre_rameurs,
        "rameurs": list(rameurs_disponibles.values("id", "prenom", "nom"))
    })


# =========================================================================================
# Récupération des rameurs en fonction du bateau sélectionné
# =========================================================================================
# def historique_sorties(request):
#     date_debut = request.GET.get("date_debut")
    
#     sorties = Sortie.objects.filter(fin__isnull=False).order_by('-debut')  # Trie par date de début décroissante

#     if date_debut:
#         sorties = sorties.filter(debut__date=date_debut)

#     return render(request, "cahierDeSorties/historique_sorties.html", {"sorties": sorties})

PER_PAGE_CHOICES = [5, 10, 20, 50, 100]

def historique_sorties(request):
    sorties_list = Sortie.objects.all().order_by('-debut')
    date_debut = request.GET.get('date_debut')
    if date_debut:
        sorties_list = sorties_list.filter(debut__date=date_debut)

    # Récupère le nombre de sorties par page (par défaut 10)
    per_page = request.GET.get('per_page')
    try:
        per_page = int(per_page)
        if per_page not in PER_PAGE_CHOICES:
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    paginator = Paginator(sorties_list, per_page)
    page_number = request.GET.get('page')
    sorties = paginator.get_page(page_number)

    return render(request, 'cahierDeSorties/historique_sorties.html', {
        'sorties': sorties,
        'per_page_choices': PER_PAGE_CHOICES,
    })


# =========================================================================================
# Page des statistiques rameurs
# =========================================================================================
def statistiques_rameurs(request):
    rameurs = Rameur.objects.all()
    selected_rameur_id = request.GET.get('rameur_id')
    selected_year = request.GET.get('year', 'current')

    today = date.today()
    current_year = today.year if today.month >= 9 else today.year - 1  # Année scolaire en cours
    years = list(range(current_year, current_year - 5, -1))
    
    start_date, end_date = None, None

    if selected_year == 'current':
        start_date = date(current_year, 9, 1)
        end_date = date(current_year + 1, 8, 31)
    elif selected_year == 'total':
        start_date, end_date = None, None
    else:
        try:
            selected_year = int(selected_year)
            start_date = date(selected_year, 9, 1)
            end_date = date(selected_year + 1, 8, 31)
        except ValueError:
            selected_year = 'current'
            start_date = date(current_year, 9, 1)
            end_date = date(current_year + 1, 8, 31)

    # Filtrer les sorties par période
    sorties = Sortie.objects.all()
    if start_date and end_date:
        sorties = sorties.filter(debut__date__range=(start_date, end_date))

    sorties_rameur = SortieRameur.objects.filter(sortie__in=sorties)

    distance_par_mois = {month: 0 for month in range(1, 13)}

    if selected_rameur_id:
        selected_rameur = Rameur.objects.get(id=selected_rameur_id)  
        # Récupération des kilomètres par type de bateau
        km_par_type_bateau = kilometres_par_type_bateau(selected_rameur_id, int(selected_year) if selected_year != 'current' else current_year)
        sorties_rameur = sorties_rameur.filter(rameur=selected_rameur)       

        nombre_sorties = sorties_rameur.count()
        total_kilometres = sorties_rameur.aggregate(total=Sum('sortie__distance'))['total'] or 0
        moyenne_distances = total_kilometres / nombre_sorties if nombre_sorties else 0

        bateau_prefere_data = sorties_rameur.values('sortie__bateau').annotate(nb_sorties=Count('id')).order_by('-nb_sorties').first()
        bateau_prefere = Bateau.objects.get(id=bateau_prefere_data['sortie__bateau']) if bateau_prefere_data else None

        # Regrouper les distances par mois
        sorties_par_mois = sorties_rameur.values_list('sortie__debut', 'sortie__distance')
        for sortie_date, distance in sorties_par_mois:
            if sortie_date:
                mois = sortie_date.month
                distance_par_mois[mois] += float(distance or 0)  # Convertir en float pour éviter les erreurs

        return render(request, "cahierDeSorties/statistiques_rameurs.html", {
            'rameurs': rameurs,
            'selected_rameur_id': selected_rameur_id,
            'selected_rameur': selected_rameur,
            'nombre_sorties': nombre_sorties,
            'total_kilometres': round(total_kilometres, 2),
            'moyenne_distances': round(moyenne_distances, 2),
            'bateau_prefere': bateau_prefere,
            'years': years,
            'selected_year': selected_year,
            'distance_par_mois': list(distance_par_mois.values()),  # Envoyer les valeurs au template
            'mois_labels': [calendar.month_abbr[m] for m in range(1, 13)],  # Labels des mois
            'km_par_type_bateau': km_par_type_bateau
        })

    return render(request, "cahierDeSorties/statistiques_rameurs.html", {
        'rameurs': rameurs,
        'years': years,
        'selected_year': selected_year
    })


# =========================================================================================
# Page des statistiques bateaux
# =========================================================================================
def statistiques_bateaux(request):
    selected_year = request.GET.get('year', 'current')

    today = date.today()
    current_year = today.year if today.month >= 9 else today.year - 1
    years = list(range(current_year, current_year - 5, -1))

    start_date, end_date = None, None

    if selected_year == 'current':
        start_date = date(current_year, 9, 1)
        end_date = date(current_year + 1, 8, 31)
    elif selected_year == 'total':
        start_date, end_date = None, None
    else:
        try:
            selected_year_int = int(selected_year)
            start_date = date(selected_year_int, 9, 1)
            end_date = date(selected_year_int + 1, 8, 31)
        except ValueError:
            selected_year = 'current'
            start_date = date(current_year, 9, 1)
            end_date = date(current_year + 1, 8, 31)

    bateaux = Bateau.objects.all()
    stats = []
    for bateau in bateaux:
        sorties = Sortie.objects.filter(bateau=bateau)
        if start_date and end_date:
            sorties = sorties.filter(debut__date__range=(start_date, end_date))

        total_distance = sorties.aggregate(Sum('distance'))['distance__sum'] or 0
        nombre_sorties = sorties.count()

        stats.append({
            "nom": bateau.nom,
            "total_distance": total_distance,
            "nombre_sorties": nombre_sorties
        })

    stats = sorted(stats, key=lambda x: x['total_distance'], reverse=True)

    context = {
        "stats": stats,
        "years": years,
        "selected_year": selected_year,
    }
    return render(request, "cahierDeSorties/statistiques_bateaux.html", context)



# =========================================================================================
# Page du leaderboard
# =========================================================================================
def leaderboard(request):
    # Calculer la distance totale parcourue par chaque rameur
    rameurs_stats = (
        Rameur.objects.annotate(total_distance=Sum('sortierameur__sortie__distance'))
        .order_by('-total_distance')
    )

    return render(request, "cahierDeSorties/leaderboard.html", {"rameurs_stats": rameurs_stats})


# =========================================================================================
# Page de l'atelier
# =========================================================================================
def atelier(request):
    incidents_en_cours = Incident.objects.filter(date_cloture__isnull=True).order_by('-date_creation')
    incidents_clotures = Incident.objects.filter(date_cloture__isnull=False).order_by('-date_cloture')

    context = {
        "incidents_en_cours": incidents_en_cours,
        "incidents_clotures": incidents_clotures
    }
    return render(request, "cahierDeSorties/atelier.html", context)