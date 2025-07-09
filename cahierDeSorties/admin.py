from django.contrib import admin
from .models import Rameur, Bateau, Sortie, SortieRameur, Incident

admin.site.register(Rameur)
admin.site.register(Bateau)
admin.site.register(Sortie)
admin.site.register(SortieRameur)
admin.site.register(Incident)