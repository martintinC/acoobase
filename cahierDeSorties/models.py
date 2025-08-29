from django.db import models

class Rameur(models.Model):
    GENRE_CHOICES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
    ]
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    actif = models.BooleanField(default=True)
    genre = models.CharField(
        max_length=1,
        choices=GENRE_CHOICES,
        default='H',  # Par défaut, on met 'Homme'
    )


    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Bateau(models.Model):
    nom = models.CharField(max_length=100)
    nombre_rameurs = models.IntegerField()
    couple = models.BooleanField(default=False)
    barre = models.BooleanField(default=False)
    en_sortie = models.BooleanField(default=False)
    en_reparation = models.BooleanField(default=False)
    prive = models.BooleanField(default=False)
    immobile = models.BooleanField(default=False)
    marque = models.CharField(max_length=100, blank=True, null=True)
    annee = models.PositiveIntegerField(blank=True, null=True)
    portance = models.PositiveIntegerField(blank=True, null=True)
    materiau = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Bateaux"  # Pluriel correct dans l'admin

    def __str__(self):
        return self.nom

class Sortie(models.Model):
    distance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bateau = models.ForeignKey(Bateau, on_delete=models.CASCADE)
    debut = models.DateTimeField()
    fin = models.DateTimeField(null=True, blank=True)
    couple = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Si la sortie est en cours de création et que le bateau est défini,
        # on copie la valeur du champ 'couple' du bateau dans le champ 'couple' de la sortie
        if not self.pk:  # Si la sortie n'a pas encore été enregistrée
            self.couple = self.bateau.couple  # Valeur du bateau
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sortie {self.id} - {self.bateau.nom} - {self.debut.strftime('%d/%m/%Y %H:%M')}"


class SortieRameur(models.Model):
    sortie = models.ForeignKey(Sortie, on_delete=models.CASCADE)
    rameur = models.ForeignKey(Rameur, on_delete=models.CASCADE)

    def __str__(self):
        return f"ID {self.id} - {self.rameur.prenom} {self.rameur.nom} - sortie {self.sortie.id} "

class Incident(models.Model):
    bateau = models.ForeignKey(Bateau, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture = models.DateTimeField(null=True, blank=True)
    createur = models.ForeignKey(Rameur, on_delete=models.CASCADE)
    description = models.TextField()
    commentaire = models.TextField(blank=True, null=True)

    def est_cloture(self):
        return self.date_cloture is not None

    def __str__(self):
        return f"Incident {self.id} - {self.bateau.nom} ({'Clôturé' if self.est_cloture() else 'En cours'})"