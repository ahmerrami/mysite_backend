from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import Widget  # ForeignKeyWidget
from django.core.mail import EmailMessage
from .models import Ville, Periode, Stage

# Register your models here.
admin.site.register(Ville)
admin.site.register(Periode)

class PeriodeWidget(Widget):
    def render(self, value, obj=None):
        return value.periode if value else ''

# Define a custom resource for Stage
class StageResource(resources.ModelResource):
    ville = fields.Field(attribute='ville__ville', column_name='Ville')

    class Meta:
        model = Stage
        fields = ('civilite', 'nom', 'prenom', 'cin', 'dateN', 'tel', 'email', 'adress', 'ville', 'niveau', 'ecole', 'specialite', 'villeEcole', 'selectedPeriode', 'created_at', 'cv', 'lettre', 'isChecked', 'traite', 'commentaire')
        export_order = fields

def send_mass_email(modeladmin, request, queryset):
    for stage in queryset:
        sujet = 'Candidature de stage'
        message = (
            f'Suite à votre demande de stage sur www.supratourstravel.com, vous êtes invités à l\'entretient à la gare ONCF de {stage.ville} le xx/xx/2024.\n\n'
            f'Détails du stage :\n'
            f'Nom : {stage.nom}\n'
            f'Prénom : {stage.prenom}\n'
            f'Email : {stage.email}\n'
            f'Téléphone : {stage.tel}\n'
        )
        destinataires = [stage.email]  # Ajouter l'email du candidat
        cc_destinataires = []  # Vous pouvez ajouter d'autres destinataires en copie
        cci_destinataires = ['ahmederrami@gmail.com']  # Vous pouvez ajouter d'autres destinataires en copie cachée

        email = EmailMessage(
            sujet,
            message,
            'supratourstravel2009@gmail.com',
            to=destinataires,
            cc=cc_destinataires,
            bcc=cci_destinataires
        )

        try:
            email.send()
        except Exception as e:
            modeladmin.message_user(request, f"Erreur lors de l'envoi à {stage.email}: {e}", level='error')

    modeladmin.message_user(request, "Emails envoyés avec succès")

send_mass_email.short_description = "Envoyer un email aux stagiaires sélectionnés"

class StageAdmin(ImportExportModelAdmin):
    resource_class = StageResource
    list_display = ('nom', 'tel', 'niveau', 'specialite', 'ville', 'selectedPeriode', 'created_at', 'cv', 'lettre', 'traite', 'commentaire')
    list_editable = ('ville', 'selectedPeriode')
    list_filter = ('traite', 'ville', 'selectedPeriode', 'created_at')
    list_per_page = 50
    actions = [send_mass_email]  # Ajoutez l'action ici

    # Define all fields
    all_fields = ['civilite', 'nom', 'prenom', 'cin', 'dateN', 'tel', 'email', 'adress', 'ville', 'niveau', 'ecole', 'specialite', 'villeEcole', 'selectedPeriode', 'created_at', 'cv', 'lettre', 'isChecked', 'traite', 'commentaire']

    def get_readonly_fields(self, request, obj=None):
        # Check if the user is in the 'stages' group
        if request.user.groups.filter(name='stages').exists():
            return [field for field in self.all_fields if field not in ['traite', 'commentaire']]
        else:
            return self.all_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='stages').exists():
            return qs
        return qs

    def has_change_permission(self, request, obj=None):
        # Allow change permission if the user is in the allowed list
        if request.user.groups.filter(name='stages').exists():
            return True
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        # Allow view permission for all users
        return True

    search_help_text = ""  # Define a search help text, even if it is empty

admin.site.register(Stage, StageAdmin)