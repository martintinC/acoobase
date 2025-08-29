from django.shortcuts import render
from django.db.models import Count, Sum
from datetime import date
import calendar
from django.core.paginator import Paginator
from ..models import Rameur, Bateau, Sortie, SortieRameur
from ..services.statistiques import kilometres_par_type_bateau

def statistiques_rameurs(request):
    rameurs = Rameur.objects.all()
    selected_rameur_id = request.GET.get('rameur_id')
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
            selected_year = int(selected_year)
            start_date = date(selected_year, 9, 1)
            end_date = date(selected_year + 1, 8, 31)
        except ValueError:
            selected_year = 'current'
            start_date = date(current_year, 9, 1)
            end_date = date(current_year + 1, 8, 31)
    sorties = Sortie.objects.all()
    if start_date and end_date:
        sorties = sorties.filter(debut__date__range=(start_date, end_date))
    sorties_rameur = SortieRameur.objects.filter(sortie__in=sorties)
    distance_par_mois = {month: 0 for month in range(1, 13)}
    if selected_rameur_id:
        selected_rameur = Rameur.objects.get(id=selected_rameur_id)
        km_par_type_bateau = kilometres_par_type_bateau(selected_rameur_id, int(selected_year) if selected_year != 'current' else current_year)
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

    sorties = Sortie.objects.all()
    if start_date and end_date:
        sorties = sorties.filter(debut__date__range=(start_date, end_date))

    # Construction de stats_list
    stats_dict = {}
    for sortie in sorties.select_related('bateau'):
        bateau = sortie.bateau
        if bateau not in stats_dict:
            stats_dict[bateau] = {'nom': bateau.nom, 'nombre_sorties': 0, 'total_distance': 0.0}
        stats_dict[bateau]['nombre_sorties'] += 1
        stats_dict[bateau]['total_distance'] += float(sortie.distance or 0)
    stats_list = list(stats_dict.values())
    stats_list.sort(key=lambda b: b['nom'])

    # Pagination
    per_page = request.GET.get('per_page')
    try:
        per_page = int(per_page)
        if per_page not in PER_PAGE_CHOICES:
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    paginator = Paginator(stats_list, per_page)
    page_number = request.GET.get('page')
    stats_page = paginator.get_page(page_number)

    return render(request, 'cahierDeSorties/statistiques_bateaux.html', {
        'stats': stats_page,
        'years': years,
        'selected_year': selected_year,
        'per_page_choices': PER_PAGE_CHOICES,
    })