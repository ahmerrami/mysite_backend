import os
import django
from django.template.loader import render_to_string
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

try:
    from xhtml2pdf import pisa
    print("IMPORT_OK")
except ImportError as e:
    print(f"IMPORT_FAIL: {e}")
    exit(1)

template_path = 'clients/pdf/dashboard_hebdo.html'
context = {
    'start_date': '2023-01-01',
    'end_date': '2023-01-07',
    'total_leads': 100,
    'total_orders': 20,
    'client_name': 'Test Client'
}

try:
    html = render_to_string(template_path, context)
    print("TEMPLATE_OK")
except Exception as e:
    print(f"TEMPLATE_FAIL: {e}")
    exit(1)

try:
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        print(f"PDF_OK_BYTES={len(result.getvalue())}")
    else:
        print(f"PDF_FAIL: {pdf.err}")
except Exception as e:
    print(f"PDF_EXCEPTION: {e}")
