import tempfile
from datetime import date
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from apps.accounts.decorators import admin_required, manager_or_admin
from apps.accounts.models import Branch
from apps.accounts.services import get_visible_branches
from apps.clients.services import get_visible_clients
from apps.journal.services import get_visible_orders
from apps.services.models import Service

from .exporters import (
    export_clients_to_excel,
    export_orders_to_excel,
    export_services_to_excel,
)

try:
    from weasyprint import HTML
except (ImportError, OSError):  # pragma: no cover - WeasyPrint/GTK не установлен
    HTML = None


@login_required
def order_pdf(request, pk):
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)

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


@login_required
def order_docx(request, pk):
    """Бланк заказа в формате DOC (Word)."""
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)

    try:
        from docx import Document
    except ImportError:
        return HttpResponse(
            "python-docx не установлен. Установите зависимости для DOC.",
            status=500,
        )

    doc = Document()
    doc.add_heading(f"Бланк заказа № {order.number or order.pk}", level=1)

    doc.add_paragraph(f"Клиент: {order.client.fio}")
    doc.add_paragraph(f"Площадка: {order.branch.name}")
    doc.add_paragraph(f"Дата документа: {order.document_date}")

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Наименование услуги"
    hdr[1].text = "Содержание"
    hdr[2].text = "Цена"

    for item in order.items.all():
        row = table.add_row().cells
        row[0].text = item.name
        row[1].text = item.description or "—"
        row[2].text = str(item.price)

    doc.add_paragraph(f"Итого: {order.total}")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)

    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    filename = f"zayavka_{order.number or order.pk}.docx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def clients_excel(request):
    clients = get_visible_clients(request.user).select_related("branch")
    return export_clients_to_excel(clients)


@admin_required
def services_excel(request):
    services = Service.objects.all()
    return export_services_to_excel(services)


@login_required
def orders_excel(request):
    orders = get_visible_orders(request.user).prefetch_related("items")
    return export_orders_to_excel(orders)


@manager_or_admin
def report_index(request):
    branches = get_visible_branches(request.user)
    return render(request, "reports/report_index.html", {"branches": branches})


@manager_or_admin
def report_pdf(request):
    branch_id = request.GET.get("branch")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    orders = get_visible_orders(request.user)
    if branch_id:
        orders = orders.filter(branch_id=branch_id)
    if date_from:
        orders = orders.filter(document_date__gte=date_from)
    if date_to:
        orders = orders.filter(document_date__lte=date_to)

    if HTML is None:
        return HttpResponse(
            "WeasyPrint не установлен. Не удаётся сформировать отчёт.",
            status=500,
        )

    total_sum = sum(o.total for o in orders)

    html_string = render_to_string(
        "reports/report_pdf.html",
        {
            "orders": orders,
            "total_sum": total_sum,
            "branch": Branch.objects.filter(pk=branch_id).first(),
            "date_from": date_from,
            "date_to": date_to,
            "generated": date.today().isoformat(),
        },
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf(
            tmp.name
        )
        tmp.seek(0)
        content = tmp.read()

    response = HttpResponse(content, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="report.pdf"'
    return response