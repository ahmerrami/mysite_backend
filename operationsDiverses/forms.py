from django import forms

class ImportCompteForm(forms.Form):
    fichier_excel = forms.FileField(label="Sélectionner un fichier Excel")
