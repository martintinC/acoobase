from django.db.models import Sum, F, Q, Value, CharField, Case, When
from datetime import date

def kilometres_par_type_bateau(rameur_id, saison_debut_annee):
    # Saison sportive : 1er septembre N à 31 août N+1
    date_debut = date(saison_debut_annee, 9, 1)
    date_fin = date(saison_debut_annee + 1, 8, 31)

    from ..models import SortieRameur

    sorties = SortieRameur.objects.filter(
        rameur_id=rameur_id,
        sortie__debut__date__gte=date_debut,
        sortie__debut__date__lte=date_fin,
        sortie__distance__isnull=False,
    ).select_related('sortie__bateau')

    # Annoter avec les caractéristiques nécessaires
    sorties = sorties.annotate(
        nombre_rameurs=F('sortie__bateau__nombre_rameurs'),
        couple=F('sortie__couple'),  # ✅ Utilisation de sortie.couple ici
        barre=F('sortie__bateau__barre'),
    ).annotate(
        type_bateau=Case(
            When(nombre_rameurs=1, then=Value('1x')),
            When(nombre_rameurs=2, couple=True, then=Value('2x')),
            When(nombre_rameurs=2, couple=False, then=Value('2-')),
            When(nombre_rameurs=4, couple=True, barre=True, then=Value('4x+')),
            When(nombre_rameurs=4, couple=True, barre=False, then=Value('4x')),
            When(nombre_rameurs=4, couple=False, barre=True, then=Value('4+')),
            When(nombre_rameurs=4, couple=False, barre=False, then=Value('4-')),
            When(nombre_rameurs=8, couple=True, then=Value('8x')),
            When(nombre_rameurs=8, couple=False, then=Value('8+')),
            default=Value('Autre'),
            output_field=CharField()
        )
    )

    # Grouper par type de bateau et sommer la distance
    resultats = sorties.values('type_bateau').annotate(
        total_km=Sum('sortie__distance')
    ).order_by('type_bateau')

    return resultats
