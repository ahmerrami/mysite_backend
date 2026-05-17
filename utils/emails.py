from io import BytesIO

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from xhtml2pdf import pisa

from clients.services import get_weekly_dashboard_data
from fournisseurs.services import (
    get_suppliers_invoices_data,
    get_suppliers_overdue_invoices_data,
    get_suppliers_unsettled_po_data,
)

def generer_et_envoyer_dashboard_hebdo():
    # 1. Collecter les données de vos modèles
    data = get_weekly_dashboard_data()
    
    # 2. Rendre le template HTML avec les données
    html_string = render_to_string('clients/pdf/dashboard_hebdo.html', {'data': data})
    
    # 3. Convertir le HTML en PDF avec xhtml2pdf/reportlab
    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(src=html_string, dest=pdf_buffer, encoding='utf-8')
    if pdf_status.err:
        raise ValueError("La generation du PDF dashboard a echoue avec xhtml2pdf.")

    pdf_file = pdf_buffer.getvalue()
    
    # 4. Préparer l'email
    sujet = f"Rapport Hebdomadaire Recouvrement - {data['date_generation'].strftime('%d/%m/%Y')}"
    corps_email = (
        "Bonjour,\n\nVeuillez trouver ci-joint le tableau de bord hebdomadaire "
        "relatif au suivi des clients, encaissements et retards de paiement.\n\nCordialement."
    )

    to_emails = [email.strip() for email in config('TO_DESTINATAIRES_BC', default='').split(',') if email.strip()]
    if not to_emails:
        raise ValueError("Aucun destinataire configure dans TO_DESTINATAIRES_BC.")
    
    email = EmailMessage(
        subject=sujet,
        body=corps_email,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )
    
    # 5. Attacher le PDF généré en mémoire
    nom_fichier = f"dashboard_hebdo_{data['date_generation'].strftime('%Y_%m_%d')}.pdf"
    email.attach(nom_fichier, pdf_file, 'application/pdf')
    
    # 6. Envoyer !
    return email.send()


def generer_et_envoyer_factures_impayees_fournisseurs():
    """Génère et envoie le rapport des factures impayées aux fournisseurs."""
    # 1. Collecter les données
    data = get_suppliers_invoices_data()
    
    # 2. Rendre le template HTML
    html_string = render_to_string('fournisseurs/pdf/invoices_impayees.html', {'data': data})
    
    # 3. Convertir en PDF
    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(src=html_string, dest=pdf_buffer, encoding='utf-8')
    if pdf_status.err:
        raise ValueError("La generation du PDF factures impayees a echoue avec xhtml2pdf.")

    pdf_file = pdf_buffer.getvalue()
    
    # 4. Préparer l'email
    sujet = f"Suivi Factures Impayées - {data['date_generation'].strftime('%d/%m/%Y')}"
    corps_email = (
        "Bonjour,\n\nVeuillez trouver ci-joint le rapport détaillé des factures "
        "impayées auprès de vos fournisseurs.\n\nCordialement."
    )

    to_emails = [email.strip() for email in config('TO_DESTINATAIRES_FACTURES', default='').split(',') if email.strip()]
    if not to_emails:
        raise ValueError("Aucun destinataire configure dans TO_DESTINATAIRES_FACTURES.")
    
    email = EmailMessage(
        subject=sujet,
        body=corps_email,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )
    
    # 5. Attacher le PDF
    nom_fichier = f"factures_impayees_{data['date_generation'].strftime('%Y_%m_%d')}.pdf"
    email.attach(nom_fichier, pdf_file, 'application/pdf')
    
    # 6. Envoyer
    return email.send()


def generer_et_envoyer_factures_depassement_fournisseurs():
    """Génère et envoie le rapport des factures dépassement d'échéance."""
    # 1. Collecter les données
    data = get_suppliers_overdue_invoices_data()
    
    # 2. Rendre le template HTML
    html_string = render_to_string('fournisseurs/pdf/invoices_depassement.html', {'data': data})
    
    # 3. Convertir en PDF
    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(src=html_string, dest=pdf_buffer, encoding='utf-8')
    if pdf_status.err:
        raise ValueError("La generation du PDF factures depassement a echoue avec xhtml2pdf.")

    pdf_file = pdf_buffer.getvalue()
    
    # 4. Préparer l'email
    sujet = f"Factures - Dépassement d'Échéance - {data['date_generation'].strftime('%d/%m/%Y')}"
    corps_email = (
        "Bonjour,\n\nVeuillez trouver ci-joint le rapport des factures dont l'échéance "
        "a dépassé ou s'approche (5 prochains jours).\n\nAction requise.\n\nCordialement."
    )

    to_emails = [email.strip() for email in config('TO_DESTINATAIRES_FACTURES', default='').split(',') if email.strip()]
    if not to_emails:
        raise ValueError("Aucun destinataire configure dans TO_DESTINATAIRES_FACTURES.")
    
    email = EmailMessage(
        subject=sujet,
        body=corps_email,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )
    
    # 5. Attacher le PDF
    nom_fichier = f"factures_depassement_{data['date_generation'].strftime('%Y_%m_%d')}.pdf"
    email.attach(nom_fichier, pdf_file, 'application/pdf')
    
    # 6. Envoyer
    return email.send()


def generer_et_envoyer_bc_non_soldes_fournisseurs():
    """Génère et envoie le rapport des bons de commande non soldés."""
    # 1. Collecter les données
    data = get_suppliers_unsettled_po_data()
    
    # 2. Rendre le template HTML
    html_string = render_to_string('fournisseurs/pdf/bc_non_soldes.html', {'data': data})
    
    # 3. Convertir en PDF
    pdf_buffer = BytesIO()
    pdf_status = pisa.CreatePDF(src=html_string, dest=pdf_buffer, encoding='utf-8')
    if pdf_status.err:
        raise ValueError("La generation du PDF BC non soldes a echoue avec xhtml2pdf.")

    pdf_file = pdf_buffer.getvalue()
    
    # 4. Préparer l'email
    sujet = f"Bons de Commande Non Soldés - {data['date_generation'].strftime('%d/%m/%Y')}"
    corps_email = (
        "Bonjour,\n\nVeuillez trouver ci-joint le rapport hebdomadaire des bons de commande "
        "non soldés avec détail de suivi de facturation.\n\nCordialement."
    )

    to_emails = [email.strip() for email in config('TO_DESTINATAIRES_BC', default='').split(',') if email.strip()]
    if not to_emails:
        raise ValueError("Aucun destinataire configure dans TO_DESTINATAIRES_BC.")
    
    email = EmailMessage(
        subject=sujet,
        body=corps_email,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )
    
    # 5. Attacher le PDF
    nom_fichier = f"bc_non_soldes_{data['date_generation'].strftime('%Y_%m_%d')}.pdf"
    email.attach(nom_fichier, pdf_file, 'application/pdf')
    
    # 6. Envoyer
    return email.send()