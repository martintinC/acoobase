from django.urls import path
from django.shortcuts import redirect
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
    creer_incident,
    cloturer_incident,
    editer_incident,
    armer_mode,
)

urlpatterns = [
    path('', lambda request: redirect('sorties_en_cours', permanent=False)),  # Redirige la racine vers /sorties/
    path('sorties/sorties-en-cours', sorties_en_cours, name='sorties_en_cours'),  # Page des sorties en cours
    path('sorties/ajouter/', ajouter_sortie, name='ajouter_sortie'),
    path('sorties/supprimer-sortie/<int:sortie_id>/', supprimer_sortie, name='supprimer_sortie'),
    path('sorties/valider-sortie/<int:sortie_id>/', valider_sortie, name='valider_sortie'),
    path('sorties/historique/', historique_sorties, name='historique_sorties'),
    path('rameurs/get-rameurs/<int:bateau_id>/', get_rameurs, name='get_rameurs'),
    path('rameurs/statistiques-rameurs/', statistiques_rameurs, name='statistiques_rameurs'),
    path('rameurs/leaderboard/', leaderboard, name='leaderboard'),
    path('bateaux/', statistiques_bateaux, name='statistiques_bateaux'),
    path('bateaux/armer_mode/<int:bateau_id>/<str:mode>/', armer_mode, name='armer_mode'),
    path('atelier/', atelier, name='atelier'),
    path('atelier/creer-incident/', creer_incident, name='creer_incident'),
    path('atelier/cloturer-incident/<int:incident_id>/', cloturer_incident, name='cloturer_incident'),
    path('atelier/editer-incident/<int:incident_id>/', editer_incident, name='editer_incident'),
]