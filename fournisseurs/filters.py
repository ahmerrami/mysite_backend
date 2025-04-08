# filters.py
from django.db.models import Q
from .models import Facture

from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

def get_factures_queryset(beneficiaire_id=None, ordre_virement_id=None):
    """
    Retourne un queryset de factures filtrées en fonction du bénéficiaire et de l'ordre de virement.
    """
    if not beneficiaire_id:
        return Facture.objects.none()

    return Facture.objects.filter(
        Q(beneficiaire_id=beneficiaire_id, ordre_virement__isnull=True) |
        Q(ordre_virement_id=ordre_virement_id)
    )

class DateRangeFilter(admin.SimpleListFilter):
    title = _('Date range')  # Titre par défaut, peut être écrasé dans la sous-classe
    parameter_name = 'date_range'  # Paramètre par défaut, peut être écrasé
    date_field = None  # Doit être défini dans la sous-classe ou via le constructeur

    def lookups(self, request, model_admin):
        return (
            ('past30', _('Last 30 days')),
            ('30', _('Next 30 days')),
            ('60', _('Next 60 days')),
            ('90', _('Next 90 days')),
        )

    def queryset(self, request, queryset):
        if not self.value() or not self.date_field:
            return queryset

        today = timezone.now().date()
        days = int(self.value().replace('past', '-'))

        if days > 0:
            # Filtre futur (next X days)
            end_date = today + timedelta(days=days)
            return queryset.filter(
                **{f'{self.date_field}__gte': today,
                   f'{self.date_field}__lte': end_date}
            )
        else:
            # Filtre passé (last X days)
            start_date = today + timedelta(days=days)  # days est négatif ici
            return queryset.filter(
                **{f'{self.date_field}__gte': start_date,
                   f'{self.date_field}__lte': today}
            )

    def __init__(self, request, params, model, model_admin, field_name=None):
        if field_name:
            self.date_field = field_name
            self.parameter_name = f'{field_name}_range'
            self.title = _('Date range: %s') % model._meta.get_field(field_name).verbose_name
        super().__init__(request, params, model, model_admin)