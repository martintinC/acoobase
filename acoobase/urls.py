from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('sorties_en_cours', permanent=False)),  # Redirige la racine vers la page des sorties
    path('', include('cahierDeSorties.urls')),  # Inclusion des routes de cahierDeSorties
]