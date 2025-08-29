from django.shortcuts import render
from django.core.paginator import Paginator
from ..models import Sortie

PER_PAGE_CHOICES = [5, 10, 20, 50, 100]

def historique_sorties(request):
    sorties_list = Sortie.objects.all().order_by('-debut')
    date_debut = request.GET.get('date_debut')
    if date_debut:
        sorties_list = sorties_list.filter(debut__date=date_debut)
    per_page = request.GET.get('per_page', 5)
    try:
        per_page = int(per_page)
        if per_page not in PER_PAGE_CHOICES:
            per_page = 5
    except (TypeError, ValueError):
        per_page = 5
    paginator = Paginator(sorties_list, per_page)
    page_number = request.GET.get('page')
    sorties = paginator.get_page(page_number)
    return render(request, 'cahierDeSorties/historique_sorties.html', {
        'sorties': sorties,
        'per_page_choices': PER_PAGE_CHOICES,
    })