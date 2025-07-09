from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cahierDeSorties/', include('cahierDeSorties.urls')),  # Inclusion des routes de cahierDeSorties
]
