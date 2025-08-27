from django.urls import path
from .views import (
    sorties_en_cours,
    ajouter_sortie,
    get_rameurs,
    supprimer_sortie,
    valider_sortie,
    historique_sorties,
    statistiques_rameurs,
    statistiques_bateaux,
    leaderboard,
    atelier,
)

urlpatterns = [
    path('sorties/', sorties_en_cours, name='sorties_en_cours'),  # Page des sorties en cours
    path("sorties/ajouter/", ajouter_sortie, name="ajouter_sortie"),  # URL pour ajouter une sortie
    path('get_rameurs/<int:bateau_id>/', get_rameurs, name='get_rameurs'),  # URL pour obtenir les rameurs
    path("supprimer_sortie/<int:sortie_id>/", supprimer_sortie, name="supprimer_sortie"),
    path('valider_sortie/<int:sortie_id>/', valider_sortie, name='valider_sortie'),
    path('historique/', historique_sorties, name='historique_sorties'),
    path('statistiques_rameurs/', statistiques_rameurs, name='statistiques_rameurs'),
    path('statistiques_bateaux/', statistiques_bateaux, name='statistiques_bateaux'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path("atelier/", atelier, name="atelier"),
]