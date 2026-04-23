from django.contrib import admin
from .models import Ville, Periode, Stage, Candidat, ValidationCode, Candidature

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_debut', 'date_fin')
    search_fields = ('nom',)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'actif')
    search_fields = ('titre',)
    filter_horizontal = ('periodes', 'villes')

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'telephone', 'niveau_etudes', 'ecole', 'email_valide', 'telephone_valide', 'date_inscription')
    search_fields = ('prenom', 'nom', 'email', 'telephone', 'ecole')
    list_filter = ('email_valide', 'telephone_valide', 'niveau_etudes')

@admin.register(ValidationCode)
class ValidationCodeAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'code', 'type', 'created_at', 'is_valid')
    search_fields = ('candidat__nom', 'candidat__prenom', 'code')
    list_filter = ('type', 'is_valid')

@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'stage', 'periode', 'ville', 'date_soumission', 'statut')
    search_fields = ('candidat__nom', 'candidat__prenom', 'stage__titre')
    list_filter = ('statut', 'periode', 'ville', 'stage')
