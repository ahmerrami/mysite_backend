from io import BytesIO

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from decouple import config
from xhtml2pdf import pisa

from clients.services import get_weekly_dashboard_data

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
    email.send()