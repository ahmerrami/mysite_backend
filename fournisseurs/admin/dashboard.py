# /fournisseurs/admin/dashboard.py
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Case, When, IntegerField, Sum, Q
from django.shortcuts import render
from django.db import models
from django.db.models import F
from fournisseurs.models.facture_model import Facture, Beneficiaire

def get_tableau_bord_data():
    # Définir les dates de référence
    aujourdhui = timezone.now().date()
    une_semaine = aujourdhui + timedelta(days=7)
    deux_semaines = aujourdhui + timedelta(days=14)
    un_mois = aujourdhui + timedelta(days=30)

    # Filtrer les factures en instance de paiement (statut différent de 'payee')
    factures = Facture.objects.exclude(statut='payee')

    # Calculer les totaux globaux
    total_global = factures.aggregate(
        factures_en_retard=Count(
            Case(
                When(Q(date_echeance__lt=aujourdhui), then=1),
                output_field=IntegerField()
            )
        ),
        montant_retard=Sum(
            Case(
                When(Q(date_echeance__lt=aujourdhui), then=F('mnt_net_apayer')),
                output_field=models.DecimalField()
            )
        ),
        moins_une_semaine=Count(
            Case(
                When(
                    Q(date_echeance__gte=aujourdhui) & Q(date_echeance__lte=une_semaine),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_une_semaine=Sum(
            Case(
                When(
                    Q(date_echeance__gte=aujourdhui) & Q(date_echeance__lte=une_semaine),
                    then=F('mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        moins_deux_semaines=Count(
            Case(
                When(
                    Q(date_echeance__gt=une_semaine) & Q(date_echeance__lte=deux_semaines),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_deux_semaines=Sum(
            Case(
                When(
                    Q(date_echeance__gt=une_semaine) & Q(date_echeance__lte=deux_semaines),
                    then=F('mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        moins_un_mois=Count(
            Case(
                When(
                    Q(date_echeance__gt=deux_semaines) & Q(date_echeance__lte=un_mois),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_un_mois=Sum(
            Case(
                When(
                    Q(date_echeance__gt=deux_semaines) & Q(date_echeance__lte=un_mois),
                    then=F('mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        plus_un_mois=Count(
            Case(
                When(Q(date_echeance__gt=un_mois), then=1),
                output_field=IntegerField()
            )
        ),
        montant_plus_un_mois=Sum(
            Case(
                When(Q(date_echeance__gt=un_mois), then=F('mnt_net_apayer')),
                output_field=models.DecimalField()
            )
        ),
        total=Count('id'),
        montant_total=Sum(
            Case(
                When(~Q(statut='payee'), then=F('mnt_net_apayer')),
                output_field=models.DecimalField()
            )
        )
    )

    # Annoter chaque bénéficiaire avec les comptages par période d'échéance
    fournisseurs = Beneficiaire.objects.filter(
        factures_beneficiaire__in=factures
    ).distinct().annotate(
        factures_en_retard = Count(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__lt=aujourdhui) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            ),
        ),
        montant_retard=Sum(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__lt=aujourdhui) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        moins_une_semaine=Count(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gte=aujourdhui) &
                    Q(factures_beneficiaire__date_echeance__lte=une_semaine) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_une_semaine=Sum(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gte=aujourdhui) &
                    Q(factures_beneficiaire__date_echeance__lte=une_semaine) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        moins_deux_semaines=Count(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=une_semaine) &
                    Q(factures_beneficiaire__date_echeance__lte=deux_semaines) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_deux_semaines=Sum(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=une_semaine) &
                    Q(factures_beneficiaire__date_echeance__lte=deux_semaines) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        moins_un_mois=Count(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=deux_semaines) &
                    Q(factures_beneficiaire__date_echeance__lte=un_mois) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_moins_un_mois=Sum(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=deux_semaines) &
                    Q(factures_beneficiaire__date_echeance__lte=un_mois) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        plus_un_mois=Count(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=un_mois) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_plus_un_mois=Sum(
            Case(
                When(
                    Q(factures_beneficiaire__date_echeance__gt=un_mois) &
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        ),
        total=Count(
            Case(
                When(
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=1
                ),
                output_field=IntegerField()
            )
        ),
        montant_total=Sum(
            Case(
                When(
                    ~Q(factures_beneficiaire__statut='payee'),
                    then=F('factures_beneficiaire__mnt_net_apayer')
                ),
                output_field=models.DecimalField()
            )
        )
    ).order_by('raison_sociale')

    return {
        'fournisseurs': fournisseurs,
        'total_global': total_global,
        'aujourdhui': aujourdhui
    }

def tableau_bord_view(request, admin_site):
    """Vue pour afficher le tableau de bord"""
    data = get_tableau_bord_data()
    
    context = {
        **admin_site.each_context(request),
        **data,
        'title': 'Tableau de bord',
        'opts': Facture._meta,
    }

    return render(request, 'admin/fournisseurs/tableau_bord_fournisseurs.html', context)