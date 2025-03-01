# views.py
import os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum
import json
from decimal import Decimal
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

from .filters import get_factures_queryset
from .models import Beneficiaire, CompteTresorerie, Contrat, OrdreVirement, Facture

def get_beneficiaires(request):
    type_ov = request.GET.get('type_ov')
    societe = get_object_or_404(Beneficiaire, raison_sociale=settings.SOCIETE)

    beneficiaires = Beneficiaire.objects.exclude(id=societe.id) if type_ov == 'Virement' else (
        Beneficiaire.objects.filter(id=societe.id) if type_ov == 'Transfert' else Beneficiaire.objects.all()
    )

    data = {beneficiaire.id: str(beneficiaire) for beneficiaire in beneficiaires}
    return JsonResponse(data)

def get_comptes_tresorerie(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')

    if not beneficiaire_id or not beneficiaire_id.isdigit():
        return JsonResponse({})

    comptes_tresorerie = CompteTresorerie.objects.filter(beneficiaire_id=beneficiaire_id)
    data = {compte.id: str(compte) for compte in comptes_tresorerie}
    return JsonResponse(data)

def get_factures_all(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')
    ordre_virement_id = request.GET.get('ordre_virement_id')

    factures = get_factures_queryset(beneficiaire_id, ordre_virement_id).values(
        'id', 'num_facture', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement'
    )

    return JsonResponse(list(factures), safe=False)

def get_contrats_all(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')

    if not beneficiaire_id or not beneficiaire_id.isdigit():
        return JsonResponse({})

    contrats = Contrat.objects.filter(beneficiaire_id=beneficiaire_id)
    data = {contrat.id: str(contrat) for contrat in contrats}
    return JsonResponse(data)

    #contrats = get_contrats_queryset(beneficiaire_id).values(
    #    'id', 'numero_contrat', 'montant_HT', 'taux_de_TVA', 'moe'
    #)

    #return JsonResponse(list(contrats), safe=False)

def update_montant_ordre_virement(request, ordre_virement_id):
    ordre_virement = get_object_or_404(OrdreVirement, id=ordre_virement_id)
    total = ordre_virement.factures_ov.aggregate(total=Sum('mnt_net_apayer'))['total'] or Decimal('0.00')

    ordre_virement.montant = total
    ordre_virement.save(update_fields=['montant'])

    return JsonResponse({'success': True, 'montant': str(total)})

@csrf_exempt
@require_POST
def update_facture_association(request):
    try:
        data = json.loads(request.body)
        facture_id = data.get('facture_id')
        ordre_virement_id = data.get('ordre_virement_id')
        is_associated = data.get('is_associated')

        if not isinstance(facture_id, int) or not isinstance(ordre_virement_id, int) or is_associated is None:
            return JsonResponse({'success': False, 'error': 'Paramètres invalides'}, status=400)

        facture = get_object_or_404(Facture, id=facture_id)
        ordre_virement = get_object_or_404(OrdreVirement, id=ordre_virement_id)

        facture.ordre_virement = ordre_virement if is_associated else None
        facture.save()

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def generate_ov_pdf(request, ordre_virement_id):
    ordre_virement = get_object_or_404(OrdreVirement, id=ordre_virement_id)

    if not ordre_virement.compte_tresorerie_emetteur or not ordre_virement.beneficiaire:
        return JsonResponse({'success': False, 'error': 'Informations bancaires incomplètes'}, status=400)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # **Ajouter le logo**
    logo_path = os.path.join(settings.MEDIA_ROOT, 'img', 'Logo ST PNG.png')  # Chemin absolu vers le logo
    if os.path.exists(logo_path):  # Vérifier si le fichier existe
        logo = ImageReader(logo_path)
        logo_width, logo_height = 50 * mm, 20 * mm  # Redimensionner le logo (50mm de large, 20mm de haut)
        p.drawImage(logo, 50, height - 50 - logo_height, width=logo_width, height=logo_height, mask='auto')
    else:
        print(f"Logo non trouvé à l'emplacement : {logo_path}")  # Avertissement si le logo est manquant

    # 📄 **Première page : Détails de l'ordre de virement**
    y_position = height - 100  # Départ du texte
    line_spacing = 35  # Espacement des lignes
    y_position -= line_spacing

    # Définir la police en gras
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor("blue")
    p.drawString(200, y_position, f"Ordre de virement n° : {ordre_virement.reference}")
    p.setFillColor("black")
    p.setFont("Helvetica", 12)
    y_position -= line_spacing
    y_position -= line_spacing/2
    p.drawString(100, y_position, "Guichet : ")
    p.setFillColor("blue")
    p.drawString(180, y_position, ordre_virement.compte_tresorerie_emetteur.banque)
    p.setFillColor("black")
    y_position -= line_spacing
    p.drawString(100, y_position, "Nom du donneur d’ordre : ")
    p.setFillColor("blue")
    p.drawString(270, y_position, ordre_virement.compte_tresorerie_emetteur.beneficiaire.raison_sociale)
    p.setFillColor("black")
    y_position -= line_spacing
    p.drawString(100, y_position, "Veuillez virer par le débit de mon compte n° : ")
    p.setFillColor("blue")
    p.drawString(370, y_position, ordre_virement.compte_tresorerie_emetteur.rib)
    p.setFillColor("black")
    y_position -= line_spacing
    p.drawString(100, y_position, "La somme de : ")
    p.setFillColor("blue")
    p.drawString(200, y_position, f"{ordre_virement.montant} DH")
    p.setFillColor("black")
    y_position -= line_spacing
    p.drawString(100, y_position, "En faveur de : ")
    p.setFillColor("blue")
    p.drawString(200, y_position, ordre_virement.beneficiaire.raison_sociale)
    p.setFillColor("black")
    y_position -= line_spacing

    if ordre_virement.compte_tresorerie.type_compte == "bancaire":
        p.drawString(100, y_position, "Domicilié chez : ")
        p.setFillColor("blue")
        p.drawString(230, y_position, ordre_virement.compte_tresorerie.banque)
        p.setFillColor("black")
        y_position -= line_spacing
        p.drawString(100, y_position, "Compte n° : ")
        p.setFillColor("blue")
        p.drawString(200, y_position, ordre_virement.compte_tresorerie.rib)
        p.setFillColor("black")
    elif ordre_virement.compte_tresorerie.type_compte == "caisse":
        p.drawString(100, y_position, "Nom caisse : ")
        p.setFillColor("blue")
        p.drawString(200, y_position, ordre_virement.compte_tresorerie.nom_caisse)
        p.setFillColor("black")
        y_position -= line_spacing
        p.drawString(100, y_position, "Détenteur caisse : ")
        p.setFillColor("blue")
        p.drawString(230, y_position, ordre_virement.compte_tresorerie.detenteur_caisse)
        p.setFillColor("black")

    y_position -= line_spacing
    # Générer la liste formatée des factures
    factures = ordre_virement.factures_ov.all()
    factures_text = ", ".join(
        f"({facture.num_facture}, {facture.montant_ttc:.2f} DH, {facture.mnt_net_apayer:.2f} DH)"
        for facture in factures
    )

    # Vérifier si la liste est vide
    p.drawString(100, y_position, "Instruction particulières : ")
    instruction_color = "black" if not factures_text else "blue"
    y_position -= line_spacing

    # Définir la couleur pour le texte des factures
    p.setFillColor(instruction_color)

    # Découper factures_text en plusieurs lignes si nécessaire
    max_chars_per_line = 80  # Ajuster en fonction de la largeur disponible
    lines = []
    while len(factures_text) > max_chars_per_line:
        split_index = factures_text[:max_chars_per_line].rfind(",")  # Trouver la dernière virgule avant la limite
        if split_index == -1:  # Si aucune virgule trouvée, couper directement
            split_index = max_chars_per_line
        lines.append(factures_text[:split_index])
        factures_text = factures_text[split_index + 1:]

    lines.append(factures_text)  # Ajouter la dernière partie restante

    # Afficher chaque ligne séparément avec un léger décalage
    for line in lines:
        p.drawString(120, y_position, line.strip())
        y_position -= line_spacing/2
    y_position -= line_spacing/2

    # Remettre la couleur en noir pour les textes suivants
    p.setFillColor("black")

    p.drawString(100, y_position, "Mode de virement : ")
    p.setFillColor("blue")
    p.drawString(250, y_position, "Normal")
    p.setFillColor("black")

    # Espace pour signatures
    y_position -= 2 * line_spacing
    p.line(100, y_position, 250, y_position)  # Signature 1
    p.drawString(100, y_position - 20, "Signature Trésorier")
    p.line(350, y_position, 500, y_position)  # Signature 2
    p.drawString(350, y_position - 20, "Signature Donneur d'Ordre")

    p.showPage()

    # 📄 **Seconde page : Liste des factures**
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, f"Annexe : Liste des factures liées à l'OV {ordre_virement.reference}")
    p.setFont("Helvetica", 12)
    y_position = 770

    total_ttc = 0
    total_net = 0

    if not factures.exists():
        p.drawString(100, y_position, "Aucune facture associée à cet ordre de virement.")
    else:
        # 🏷️ **En-tête du tableau**
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "Numéro Facture")
        p.drawString(220, y_position, "Date Facture")
        p.drawString(340, y_position, "Montant TTC (DH)")
        p.drawString(460, y_position, "Net à Payer (DH)")
        p.line(100, y_position - 5, 500, y_position - 5)
        y_position -= 25

        p.setFont("Helvetica", 12)
        for facture in factures:
            if y_position < 100:  # Nouvelle page si nécessaire
                p.showPage()
                p.setFont("Helvetica-Bold", 12)
                p.drawString(100, 800, "Annexe (suite) : Liste des factures liées")
                y_position = 770

            p.drawString(100, y_position, facture.num_facture)
            p.drawString(220, y_position, facture.date_facture.strftime('%d/%m/%Y'))
            p.drawString(340, y_position, f"{facture.montant_ttc:.2f}")
            p.drawString(460, y_position, f"{facture.mnt_net_apayer:.2f}")

            total_ttc += facture.montant_ttc
            total_net += facture.mnt_net_apayer

            y_position -= 20

        # Vérifier si on a assez de place pour afficher le total
        if y_position < 100:
            p.showPage()
            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, 800, "Annexe (suite) : Liste des factures liées")
            y_position = 770

        # Affichage du total
        p.setFont("Helvetica-Bold", 12)
        p.line(100, y_position - 5, 500, y_position - 5)  # Ligne de séparation
        y_position -= 20
        p.drawString(100, y_position, "Total")
        p.drawString(340, y_position, f"{total_ttc:.2f}")
        p.drawString(460, y_position, f"{total_net:.2f}")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ordre_virement_{ordre_virement.reference}.pdf"'
    return response