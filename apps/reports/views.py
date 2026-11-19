import logging
import tempfile
from datetime import date
from io import BytesIO
from urllib.parse import quote

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

logger = logging.getLogger(__name__)

_PDF_FALLBACK_NOTICE = (
    '<div style="position:fixed;top:0;left:0;right:0;z-index:9999;'
    'background:#fff3cd;border-bottom:1px solid #ffecb5;color:#664d03;'
    'padding:10px 16px;font:14px/1.4 Arial,sans-serif;">'
    'Автоматическая генерация PDF на сервере недоступна. '
    'Нажмите <b>Ctrl+P</b> (на macOS — <b>Cmd+P</b>) и выберите '
    '«Сохранить как PDF» в диалоге печати.'
    '</div>'
)

_PDF_FALLBACK_SCRIPT = (
    '<script>'
    'window.addEventListener("load", function () {'
    '  setTimeout(function () { window.print(); }, 400);'
    '});'
    '</script>'
)


def _pdf_response_or_fallback(request, template_name, context, filename):
    """Пробует отдать PDF через WeasyPrint, иначе — HTML с автопечатью.

    На shared-хостинге WeasyPrint может быть не установлен или не иметь
    системных библиотек (pango/cairo), поэтому вместо 500 отдаём
    готовый к печати HTML — из него браузер сохраняет PDF через Ctrl+P.
    """
    html_string = render_to_string(template_name, context, request=request)

    if HTML is not None:
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                HTML(
                    string=html_string,
                    base_url=request.build_absolute_uri("/"),
                ).write_pdf(tmp.name)
                tmp.seek(0)
                content = tmp.read()
            response = HttpResponse(content, content_type="application/pdf")
            response["Content-Disposition"] = f'inline; filename="{filename}"'
            return response
        except Exception:  # noqa: BLE001 - любые ошибки рендера PDF
            logger.exception("Не удалось сформировать PDF, отдаём HTML-версию")

    if "</body>" in html_string:
        html_string = html_string.replace(
            "</body>", _PDF_FALLBACK_NOTICE + _PDF_FALLBACK_SCRIPT + "</body>", 1
        )
    else:
        html_string += _PDF_FALLBACK_NOTICE + _PDF_FALLBACK_SCRIPT

    response = HttpResponse(html_string, content_type="text/html; charset=utf-8")
    response["Content-Disposition"] = f'inline; filename="{filename}.html"'
    return response


@login_required
def order_pdf(request, pk):
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)

    filename = f"zayavka_{order.number or order.pk}.pdf"
    return _pdf_response_or_fallback(
        request,
        "reports/order_pdf.html",
        {"order": order, "items": list(order.items.all()), "total": order.total},
        filename,
    )


@login_required
def order_docx(request, pk):
    """Заявка на оказание услуги по шаблону DOCX."""
    order = get_object_or_404(get_visible_orders(request.user), pk=pk)

    try:
        from .docx_zayavka import build_zayavka_docx
    except ImportError:
        return HttpResponse(
            "python-docx не установлен. Установите зависимости для DOC.",
            status=500,
        )

    buf = build_zayavka_docx(order)

    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    number = order.number or order.pk
    filename = f"Заявка №{number}.docx"
    response["Content-Disposition"] = (
        'attachment; filename="zayavka.docx"; '
        f"filename*=UTF-8''{quote(filename)}"
    )
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

    total_sum = sum(o.total for o in orders)

    return _pdf_response_or_fallback(
        request,
        "reports/report_pdf.html",
        {
            "orders": orders,
            "total_sum": total_sum,
            "branch": Branch.objects.filter(pk=branch_id).first(),
            "date_from": date_from,
            "date_to": date_to,
            "generated": date.today().isoformat(),
        },
        "report.pdf",
    )
