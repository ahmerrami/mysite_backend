from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import simpleSplit
from .models import OperationDiverse

def format_montant(valeur):
    """ Formate le montant avec séparateurs de milliers et deux décimales. """
    return "{:,.2f}".format(valeur).replace(",", " ") if valeur else ""

def generate_operation_pdf(request, operation_id):
    operation = get_object_or_404(OperationDiverse, id=operation_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="operation_{operation.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Opération Diverse")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"N° : {operation.id}")
    p.drawString(400, height - 100, f"Année Comptable : {operation.annee_comptable}")

    # Gestion dynamique du libellé
    max_width = 400
    libelle_lines = simpleSplit(operation.libelle, "Helvetica", 12, max_width)

    y_position = height - 130
    for i, line in enumerate(libelle_lines):
        prefix = "Libellé : " if i == 0 else "         "
        p.drawString(50, y_position, f"{prefix}{line}")
        y_position -= 20

    # Ajustement de la position après le libellé
    y_position -= 20
    p.drawString(50, y_position, f"Date : {operation.date_operation.strftime('%d/%m/%Y')}")

    # Écritures comptables
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Écritures Comptables")

    # Construire la table des imputations
    data = [["Compte", "Libellé", "Débit", "Crédit"]]
    row_heights = [25]  # Hauteur de l'en-tête

    for ecriture in operation.ecritures.all():
        compte_numero = ecriture.compte.numero
        intitule_lines = simpleSplit(ecriture.compte.intitule, "Helvetica", 10, 180)  # Largeur max 180
        max_line_height = len(intitule_lines) * 15  # Hauteur dynamique selon le nombre de lignes

        montant_debit = format_montant(ecriture.montant) if ecriture.sens_ecriture == "DEBIT" else ""
        montant_credit = format_montant(ecriture.montant) if ecriture.sens_ecriture == "CREDIT" else ""

        data.append([compte_numero, "\n".join(intitule_lines), montant_debit, montant_credit])
        row_heights.append(max_line_height)

    # Ajout de la ligne total
    total_debit = sum(e.montant for e in operation.ecritures.filter(sens_ecriture="DEBIT"))
    total_credit = sum(e.montant for e in operation.ecritures.filter(sens_ecriture="CREDIT"))
    data.append(["", "Total", format_montant(total_debit), format_montant(total_credit)])
    row_heights.append(25)  # Hauteur de la ligne des totaux

    table = Table(data, colWidths=[80, 200, 80, 80], rowHeights=row_heights)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alignement vertical
    ]))

    # Ajustement dynamique de la position de la table
    y_position -= 30
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - sum(row_heights))

    p.showPage()
    p.save()

    return response
