# admin/compte_tresorerie_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django import forms
from ..models.compte_tresorerie_model import CompteTresorerie

class CompteTresorerieAdminForm(forms.ModelForm):
    class Meta:
        model = CompteTresorerie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Masquer les champs en fonction du type_compte par défaut
        if self.instance and self.instance.pk:
            if self.instance.type_compte == 'bancaire':
                self.fields['nom_caisse'].widget.attrs['style'] = 'display: none;'
                self.fields['emplacement_caisse'].widget.attrs['style'] = 'display: none;'
                self.fields['detenteur_caisse'].widget.attrs['style'] = 'display: none;'
            elif self.instance.type_compte == 'caisse':
                self.fields['banque'].widget.attrs['style'] = 'display: none;'
                self.fields['rib'].widget.attrs['style'] = 'display: none;'
                self.fields['attestation_rib_pdf'].widget.attrs['style'] = 'display: none;'

class CompteTresorerieAdmin(ImportExportModelAdmin):
    form = CompteTresorerieAdminForm
    list_display = ('beneficiaire', 'type_compte', 'banque', 'rib', 'nom_caisse')
    list_filter = ('type_compte',)
    search_fields = ('beneficiaire__raison_sociale', 'banque', 'rib')
    readonly_fields = ('created_by','updated_by')

    class Media:
        js = ('js/compte_tresorerie.js',)  # Fichier JS pour la logique dynamique

admin.site.register(CompteTresorerie, CompteTresorerieAdmin)

