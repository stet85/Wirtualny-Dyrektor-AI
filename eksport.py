"""Eksport analizy do dokumentu Word (.docx) z prostego Markdown, ktory zwraca model.
Bez zewnetrznych bibliotek (tylko standardowa biblioteka), wiec dziala na kazdym hostingu."""
import io
import re
import zipfile
from datetime import date
from xml.sax.saxutils import escape

_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _runy(tekst, rozmiar=22, pogrubienie=False):
    wynik = []
    for i, kawalek in enumerate(tekst.split("**")):
        if not kawalek:
            continue
        b = "<w:b/>" if (pogrubienie or i % 2 == 1) else ""
        wynik.append(f'<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>{b}'
                     f'<w:sz w:val="{rozmiar}"/></w:rPr><w:t xml:space="preserve">{escape(kawalek)}</w:t></w:r>')
    return "".join(wynik)


def _akapit(tekst, rozmiar=22, pogrubienie=False, wciecie=0, przed=0):
    ind = f'<w:ind w:left="{wciecie}" w:hanging="283"/>' if wciecie else ""
    return (f'<w:p><w:pPr><w:spacing w:before="{przed}" w:after="100"/>{ind}</w:pPr>'
            f'{_runy(tekst, rozmiar, pogrubienie)}</w:p>')


def docx_bytes(tytul, tekst):
    cz = [_akapit(tytul, 40, True), _akapit(f"Wygenerowano: {date.today().isoformat()} (wirtualny dyrektor AI)", 18)]
    for linia in str(tekst).splitlines():
        s = linia.strip()
        if not s or re.fullmatch(r"[|:\-\s]+", s):
            continue
        if m := re.match(r"^(#{1,6})\s+(.*)", s):
            cz.append(_akapit(m.group(2).replace("**", ""), {1: 32, 2: 28}.get(len(m.group(1)), 24), True, przed=240))
        elif m := re.match(r"^[-*•]\s+(.*)", s):
            cz.append(_akapit("•  " + m.group(1), wciecie=567))
        elif m := re.match(r"^(\d+)[.)]\s+(.*)", s):
            cz.append(_akapit(f"{m.group(1)}.  {m.group(2)}", wciecie=567))
        else:
            cz.append(_akapit(s))
    dokument = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{_NS}"><w:body>'
                + "".join(cz) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" '
                'w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>')
    typy = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", typy)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", dokument)
    return b.getvalue()
