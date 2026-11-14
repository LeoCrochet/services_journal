"""Генерация заявки на оказание услуги по шаблону DOCX."""

from datetime import date
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.shared import Cm

TEMPLATE_PATH = Path(__file__).with_name("templates_docx") / "zayavka_template.docx"

_MONTHS_GENITIVE = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def _fmt_price(value):
    return f"{value:.2f}".replace(".", ",")


def _fmt_date(value):
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")


def _fmt_birth_date(value):
    if value is None:
        return "«___» ___________ _________ года рождения"
    return (
        f"«{value.day:02d}» {_MONTHS_GENITIVE[value.month]} "
        f"{value.year} года рождения"
    )


def _set_paragraph_text(paragraph, text):
    """Заменить текст параграфа, сохранив форматирование первого run."""
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def _set_paragraph_segments(paragraph, segments):
    """Заменить содержимое параграфа набором run'ов.

    segments — список кортежей (text, underline), где underline — булево
    значение, указывающее, нужно ли подчёркивать текст.
    """
    base = paragraph.runs[0] if paragraph.runs else None
    font_name = base.font.name if base is not None else None
    font_size = base.font.size if base is not None else None
    bold = base.font.bold if base is not None else None

    for run in list(paragraph.runs):
        run._element.getparent().remove(run._element)

    for text, underline in segments:
        run = paragraph.add_run(text)
        if font_name is not None:
            run.font.name = font_name
        if font_size is not None:
            run.font.size = font_size
        if bold is not None:
            run.font.bold = bold
        if underline:
            run.underline = True


def _replace_in_paragraph(paragraph, old, new):
    if old in paragraph.text:
        _set_paragraph_text(paragraph, paragraph.text.replace(old, new))


def _clean_template_word(doc):
    """Убрать слово «шаблон» из всех текстов документа."""
    for paragraph in doc.paragraphs:
        _replace_in_paragraph(paragraph, "шаблон", "")
        _replace_in_paragraph(paragraph, "Шаблон", "")
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    _replace_in_paragraph(paragraph, "шаблон", "")
                    _replace_in_paragraph(paragraph, "Шаблон", "")


def _decorate(value, prefix="", suffix=""):
    if not value:
        return ""
    value = value.strip()
    if prefix and value.startswith(prefix):
        prefix = ""
    if suffix and value.endswith(suffix):
        suffix = ""
    return f"{prefix}{value}{suffix}"


def _full_address(client):
    head = [
        _decorate(client.region, suffix=" область"),
        _decorate(client.district, suffix=" район"),
        _decorate(client.locality, prefix="г. "),
        _decorate(client.street, prefix="ул. "),
    ]
    tail = [
        _decorate(client.house, prefix="д. "),
        _decorate(client.building, prefix="корп. "),
        _decorate(client.apartment, prefix="кв. "),
    ]

    head = [p for p in head if p]
    tail = [p for p in tail if p]

    result = ", ".join(head)
    if tail:
        result = f"{result} {' '.join(tail)}"
    return result


def _document_label(client):
    parts = [client.document_type]
    if client.document_series:
        parts.append(client.document_series)
    if client.document_number:
        parts.append(client.document_number)
    return " ".join(p for p in parts if p)


def _remove_paragraph(paragraph):
    paragraph._element.getparent().remove(paragraph._element)


def _find_label_paragraph(doc, data_paragraph):
    """Найти следующую за строкой подписи строку-метку с «(подпись)»."""
    found = False
    for paragraph in doc.paragraphs:
        if paragraph._p is data_paragraph._p:
            found = True
            continue
        if found and "(подпись)" in paragraph.text:
            return paragraph
    return None


def _fill_signature_block(
    data_paragraph,
    label_paragraph,
    prefix,
    name,
    label_text,
    date_str,
    name_pos_cm,
    sig_pos_cm,
    date_pos_cm,
):
    """Пересобрать строку подписи и строку-метку с общими tab stops.

    Обе строки используют одинаковые позиции табуляции, поэтому
    имя/подпись/дата в строке подписи точно совпадают с метками
    «(ФИО…)», «(подпись)» и «(дата)» в строке-метке. Метка «(подпись)»
    остаётся только в строке-метке, а над ней — подчёркнутое пустое
    место для реальной подписи.
    """

    def add(paragraph, text, underline, font_name, font_size, bold):
        run = paragraph.add_run(text)
        if font_name is not None:
            run.font.name = font_name
        if font_size is not None:
            run.font.size = font_size
        if bold is not None:
            run.font.bold = bold
        if underline:
            run.underline = True
        return run

    def props(paragraph):
        base = paragraph.runs[0] if paragraph.runs else None
        return (
            base.font.name if base is not None else None,
            base.font.size if base is not None else None,
            base.font.bold if base is not None else None,
        )

    data_font, data_size, data_bold = props(data_paragraph)
    label_font, label_size, label_bold = props(label_paragraph)

    for run in list(data_paragraph.runs):
        run._element.getparent().remove(run._element)
    for run in list(label_paragraph.runs):
        run._element.getparent().remove(run._element)

    for pf in (data_paragraph.paragraph_format, label_paragraph.paragraph_format):
        pf.tab_stops.clear_all()
        pf.tab_stops.add_tab_stop(Cm(name_pos_cm), WD_TAB_ALIGNMENT.LEFT)
        pf.tab_stops.add_tab_stop(Cm(sig_pos_cm), WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Cm(date_pos_cm), WD_TAB_ALIGNMENT.RIGHT)

    # Строка подписи
    if prefix:
        add(data_paragraph, prefix, False, data_font, data_size, data_bold)
    if name_pos_cm > 0:
        add(data_paragraph, "\t", False, None, None, None)
    if name:
        add(data_paragraph, name, True, data_font, data_size, data_bold)
    else:
        add(data_paragraph, "________", False, data_font, data_size, data_bold)
    add(data_paragraph, "\t", False, None, None, None)
    add(data_paragraph, " " * 18, True, data_font, data_size, data_bold)
    add(data_paragraph, "\t", False, None, None, None)
    add(data_paragraph, date_str, True, data_font, data_size, data_bold)

    # Строка-метка
    if name_pos_cm > 0:
        add(label_paragraph, "\t", False, None, None, None)
    add(label_paragraph, label_text, False, label_font, label_size, label_bold)
    add(label_paragraph, "\t", False, None, None, None)
    add(label_paragraph, "(подпись)", False, label_font, label_size, label_bold)
    add(label_paragraph, "\t", False, None, None, None)
    add(label_paragraph, "(дата)", False, label_font, label_size, label_bold)


def build_zayavka_docx(order):
    """Сформировать заявку по шаблону и вернуть BytesIO."""
    doc = Document(str(TEMPLATE_PATH))
    client = order.client
    number = order.number or order.pk

    _clean_template_word(doc)

    # Один заголовок с номером заявки вместо двух
    header = next(
        p for p in doc.paragraphs if p.text.strip() == "Заявка на оказание услуги"
    )
    _set_paragraph_text(header, f"Заявка №{number} на оказание услуги")

    duplicate = next(p for p in doc.paragraphs if p.text.strip() == "Заявка")
    _remove_paragraph(duplicate)

    # ФИО заказчика (значение подчёркнуто)
    fio_paragraph = next(p for p in doc.paragraphs if p.text.startswith("Заказчик"))
    _set_paragraph_segments(
        fio_paragraph,
        [
            ("Заказчик: ", False),
            (client.fio, True),
        ],
    )

    # Пояснение под строкой заказчика удаляем
    hint = next(
        p
        for p in doc.paragraphs
        if p.text.strip() == "(ФИО физического лица, полностью)"
    )
    _remove_paragraph(hint)

    # Данные заказчика (значения из базы подчёркнуты)
    customer_paragraph = next(
        p for p in doc.paragraphs if "года рождения, пол" in p.text
    )
    customer_segments = [
        (_fmt_birth_date(client.birth_date), True),
        (", пол: ", False),
        (client.gender or "_____", True),
        (", гражданство: ", False),
        (client.citizenship or "____________", True),
        (", наименование документа, удостоверяющего личность: ", False),
        (_document_label(client) or "__________", True),
        (", дата выдачи: ", False),
        (_fmt_date(client.document_issue_date) or "__________", True),
        (", кем выдан: ", False),
        (client.document_issued_by or "_______________________", True),
        (", адрес регистрации по месту пребывания: ", False),
        (_full_address(client) or "__________________________________________", True),
        (", срок регистрации: ", False),
        (_fmt_date(client.registration_period) or "____________________", True),
        (", контактный телефон: ", False),
        (client.phone or "_______________________", True),
        (".", False),
    ]
    _set_paragraph_segments(customer_paragraph, customer_segments)

    # Подписи заявителя и представителя компании
    today_str = date.today().strftime("%d.%m.%Y")
    signer = ", ".join(
        p for p in [order.branch.signer_name, order.branch.signer_position] if p
    )

    customer_signature = next(
        p
        for p in doc.paragraphs
        if p.text.startswith("Заказчик:") and "(" in p.text
    )
    _fill_signature_block(
        customer_signature,
        _find_label_paragraph(doc, customer_signature),
        "Заказчик: ",
        client.fio,
        "(ФИО полностью)",
        today_str,
        name_pos_cm=3.5,
        sig_pos_cm=11.5,
        date_pos_cm=16.5,
    )

    accepted_by = next(
        p for p in doc.paragraphs if p.text.startswith("Заявку принял")
    )
    _fill_signature_block(
        accepted_by,
        _find_label_paragraph(doc, accepted_by),
        "Заявку принял: ",
        signer,
        "(ФИО, должность)",
        today_str,
        name_pos_cm=3.5,
        sig_pos_cm=11.5,
        date_pos_cm=16.5,
    )

    bare_signatures = [
        p
        for p in doc.paragraphs
        if p.text.strip().startswith("_") and "(" in p.text
    ]
    _fill_signature_block(
        bare_signatures[0],
        _find_label_paragraph(doc, bare_signatures[0]),
        None,
        client.fio,
        "(ФИО)",
        today_str,
        name_pos_cm=0,
        sig_pos_cm=11.5,
        date_pos_cm=16.5,
    )
    _fill_signature_block(
        bare_signatures[-1],
        _find_label_paragraph(doc, bare_signatures[-1]),
        None,
        signer,
        "(ФИО, должность)",
        today_str,
        name_pos_cm=0,
        sig_pos_cm=11.5,
        date_pos_cm=16.5,
    )

    # Таблица услуг (вторая таблица в шаблоне)
    if len(doc.tables) >= 2:
        table = doc.tables[1]
        for row in list(table.rows[1:]):
            row._element.getparent().remove(row._element)

        for index, item in enumerate(order.items.all(), start=1):
            row = table.add_row().cells
            row[0].text = str(index)
            row[1].text = f"{item.name}\n{item.description}".strip()
            row[2].text = _fmt_price(item.price)

        total_row = table.add_row().cells
        total_row[0].text = ""
        total_row[1].text = "Итого"
        total_row[2].text = _fmt_price(order.total)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf