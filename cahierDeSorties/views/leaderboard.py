from django.shortcuts import render
from django.db.models import Sum
from ..models import Rameur

def leaderboard(request):
    rameurs_stats = (
        Rameur.objects.annotate(total_distance=Sum('sortierameur__sortie__distance'))
        .order_by('-total_distance')
    )
    return render(request, "cahierDeSorties/leaderboard.html", {"rameurs_stats": rameurs_stats})