from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook


def _excel_response(filename):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def export_clients_to_excel(clients):
    """Экспорт списка клиентов в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Клиенты"

    headers = [
        "Код", "ФИО", "Площадка", "Дата рождения", "Пол", "Гражданство",
        "Тип документа", "Серия", "Номер", "Дата выдачи", "Кем выдан",
        "Область", "Район", "Населённый пункт", "Улица", "Дом", "Корпус",
        "Квартира", "Срок регистрации", "Телефон",
    ]
    ws.append(headers)

    for c in clients:
        ws.append([
            c.kod, c.fio, c.branch.name if c.branch else "", c.birth_date,
            c.gender, c.citizenship, c.document_type, c.document_series,
            c.document_number, c.document_issue_date, c.document_issued_by,
            c.region, c.district, c.locality, c.street, c.house, c.building,
            c.apartment, c.registration_period, c.phone,
        ])

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)

    buf = BytesIO()
    wb.save(buf)
    response = _excel_response("clients.xlsx")
    response.write(buf.getvalue())
    return response


def export_services_to_excel(services):
    """Экспорт справочника услуг в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Услуги"

    headers = ["Код", "Наименование", "Содержание", "Цена"]
    ws.append(headers)

    for s in services:
        ws.append([s.kod, s.name, s.description, s.price])

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)

    buf = BytesIO()
    wb.save(buf)
    response = _excel_response("services.xlsx")
    response.write(buf.getvalue())
    return response


def export_orders_to_excel(orders):
    """Экспорт заявок в Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Заявки"

    headers = ["Номер", "Дата", "Площадка", "Клиент", "Услуги", "Сумма"]
    ws.append(headers)

    for o in orders:
        items = "; ".join(item.name for item in o.items.all())
        ws.append([o.number, o.document_date, o.branch.name, o.client.fio, items, o.total])

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 60)

    buf = BytesIO()
    wb.save(buf)
    response = _excel_response("orders.xlsx")
    response.write(buf.getvalue())
    return response