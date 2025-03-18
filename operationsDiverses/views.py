from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import OperationDiverse

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

    p.drawString(50, height - 130, f"Libellé : {operation.libelle}")
    p.drawString(50, height - 150, f"Date : {operation.date_operation.strftime('%d/%m/%Y')}")
    #p.drawString(50, height - 170, f"Validé : {'Oui' if operation.valide else 'Non'}")

    # Tableau des écritures comptables
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 210, "Écritures Comptables")

    data = [["Compte", "Libellé", "Débit", "Crédit"]]

    for ecriture in operation.ecritures.all():
        montant_debit = ecriture.montant if ecriture.sens_ecriture == "DEBIT" else ""
        montant_credit = ecriture.montant if ecriture.sens_ecriture == "CREDIT" else ""
        data.append([ecriture.compte.numero, ecriture.compte.intitule, montant_debit, montant_credit])

    # Ajout de la ligne total
    total_debit = sum(e.montant for e in operation.ecritures.filter(sens_ecriture="DEBIT"))
    total_credit = sum(e.montant for e in operation.ecritures.filter(sens_ecriture="CREDIT"))
    data.append(["", "Total", total_debit, total_credit])

    table = Table(data, colWidths=[100, 200, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 300)

    p.showPage()
    p.save()

    return response
