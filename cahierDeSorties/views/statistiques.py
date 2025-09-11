from django.shortcuts import render
from django.db.models import Count, Sum, Q
from datetime import date
import calendar
from django.core.paginator import Paginator
from ..models import Rameur, Bateau, Sortie, SortieRameur
from ..services.statistiques import kilometres_par_type_bateau

from datetime import date
import calendar
from django.shortcuts import render
from django.db.models import Sum, Count
from cahierDeSorties.models import Rameur, Sortie, SortieRameur, Bateau
from cahierDeSorties.services.statistiques import kilometres_par_type_bateau

def statistiques_rameurs(request):
    rameurs = Rameur.objects.all().order_by('prenom', 'nom')
    selected_rameur_id = request.GET.get('rameur_id')
    selected_year = request.GET.get('year', 'current')
    today = date.today()
    current_year = today.year if today.month >= 9 else today.year - 1
    years = list(range(current_year, current_year - 5, -1))
    start_date, end_date = None, None
    year_for_stats = None  # Défini par défaut

    if selected_year == 'current':
        start_date = date(current_year, 9, 1)
        end_date = date(current_year + 1, 8, 31)
        year_for_stats = current_year
    elif selected_year == 'total':
        start_date, end_date = None, None
        year_for_stats = None
    else:
        try:
            selected_year_int = int(selected_year)
            start_date = date(selected_year_int, 9, 1)
            end_date = date(selected_year_int + 1, 8, 31)
            year_for_stats = selected_year_int
        except ValueError:
            selected_year = 'current'
            start_date = date(current_year, 9, 1)
            end_date = date(current_year + 1, 8, 31)
            year_for_stats = current_year

    sorties = Sortie.objects.all()
    if start_date and end_date:
        sorties = sorties.filter(debut__date__range=(start_date, end_date))
    sorties_rameur = SortieRameur.objects.filter(sortie__in=sorties)
    distance_par_mois = {month: 0 for month in range(1, 13)}

    if selected_rameur_id:
        selected_rameur = Rameur.objects.get(id=selected_rameur_id)
        km_par_type_bateau = kilometres_par_type_bateau(selected_rameur_id, year_for_stats)
        sorties_rameur = sorties_rameur.filter(rameur=selected_rameur)
        nombre_sorties = sorties_rameur.count()
        total_kilometres = sorties_rameur.aggregate(total=Sum('sortie__distance'))['total'] or 0
        moyenne_distances = total_kilometres / nombre_sorties if nombre_sorties else 0
        bateau_prefere_data = sorties_rameur.values('sortie__bateau').annotate(nb_sorties=Count('id')).order_by('-nb_sorties').first()
        bateau_prefere = Bateau.objects.get(id=bateau_prefere_data['sortie__bateau']) if bateau_prefere_data else None
        sorties_par_mois = sorties_rameur.values_list('sortie__debut', 'sortie__distance')
        for sortie_date, distance in sorties_par_mois:
            if sortie_date:
                mois = sortie_date.month
                distance_par_mois[mois] += float(distance or 0)
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
            'distance_par_mois': list(distance_par_mois.values()),
            'mois_labels': [calendar.month_abbr[m] for m in range(1, 13)],
            'km_par_type_bateau': km_par_type_bateau
        })
    return render(request, "cahierDeSorties/statistiques_rameurs.html", {
        'rameurs': rameurs,
        'years': years,
        'selected_year': selected_year
    })

    
PER_PAGE_CHOICES = [5, 10, 20, 50, 100]



def statistiques_bateaux(request):
    selected_year = request.GET.get('year', 'current')
    sort = request.GET.get('sort', 'nom')
    today = date.today()
    current_year = today.year if today.month >= 9 else today.year - 1
    years = list(range(current_year, current_year - 5, -1))

    # Détermination de la période
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

    sorties_filter = {}
    if start_date and end_date:
        sorties_filter = {'sortie__debut__date__range': (start_date, end_date)}

    # Annoter tous les bateaux, même sans sortie
    bateaux = Bateau.objects.annotate(
        nombre_sorties=Count('sortie', filter=Q(**sorties_filter), distinct=True),
        total_distance=Sum('sortie__distance', filter=Q(**sorties_filter))
    )

    # Tri dynamique
    if sort == "distance":
        bateaux = bateaux.order_by('-total_distance', 'nom')
    elif sort == "sorties":
        bateaux = bateaux.order_by('-nombre_sorties', 'nom')
    else:
        bateaux = bateaux.order_by('nom')

    stats_list = []
    for bateau in bateaux:
        stats_list.append({
            'id': bateau.id,
            'nom': bateau.nom,
            'nombre_sorties': bateau.nombre_sorties,
            'total_distance': round(bateau.total_distance or 0, 2),
            'marque': bateau.marque,
            'annee': bateau.annee,
            'portance': bateau.portance,
            'materiau': bateau.materiau,
            'nombre_rameurs': bateau.nombre_rameurs,
            'couple': bateau.couple,
        })

    per_page = request.GET.get('per_page', 5)
    if per_page == 'all':
        per_page = 1000
    else:
        per_page = int(per_page)

    paginator = Paginator(stats_list, per_page)
    page_number = request.GET.get('page')
    stats_page = paginator.get_page(page_number)

    return render(request, 'cahierDeSorties/statistiques_bateaux.html', {
        'stats': stats_page,
        'years': years,
        'selected_year': selected_year,
        'per_page_choices': PER_PAGE_CHOICES,
    })
    
    
    
def armer_mode(request, bateau_id, mode):
    try:
        bateau = Bateau.objects.get(id=bateau_id)
        if mode == "couple":
            bateau.couple = True
        elif mode == "pointe":
            bateau.couple = False
        else:
            return JsonResponse({"success": False, "error": "Mode inconnu"})
        bateau.save(update_fields=["couple"])
        return JsonResponse({"success": True})
    except Bateau.DoesNotExist:
        return JsonResponse({"success": False, "error": "Bateau introuvable"})