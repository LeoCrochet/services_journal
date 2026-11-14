import tempfile

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from apps.journal.models import Order

try:
    from weasyprint import HTML
except (ImportError, OSError):  # pragma: no cover - WeasyPrint/GTK не установлен (например, на Windows)
    HTML = None


@login_required
def order_pdf(request, pk):
    order = get_object_or_404(Order.objects.select_related("client"), pk=pk)

    if HTML is None:
        return HttpResponse(
            "WeasyPrint не установлен. Установите зависимости для PDF.",
            status=500,
        )

    html_string = render_to_string(
        "reports/order_pdf.html",
        {"order": order, "items": list(order.items.all()), "total": order.total},
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf(
            tmp.name
        )
        tmp.seek(0)
        content = tmp.read()

    response = HttpResponse(content, content_type="application/pdf")
    filename = f"zayavka_{order.number or order.pk}.pdf"
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response