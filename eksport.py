"""Eksport analizy do dokumentu Word (.docx) z prostego Markdown, ktory zwraca model."""
import io
import re
from datetime import date
from docx import Document


def _runy(par, tekst):
    for i, kawalek in enumerate(tekst.split("**")):
        if kawalek:
            par.add_run(kawalek).bold = (i % 2 == 1)


def docx_bytes(tytul, tekst):
    d = Document()
    d.add_heading(tytul, 0)
    d.add_paragraph(f"Wygenerowano: {date.today().isoformat()} (wirtualny dyrektor AI)")
    for linia in str(tekst).splitlines():
        s = linia.strip()
        if not s or re.fullmatch(r"[|:\-\s]+", s):
            continue
        if m := re.match(r"^(#{1,6})\s+(.*)", s):
            d.add_heading(m.group(2).replace("**", ""), min(len(m.group(1)), 3))
        elif re.match(r"^[-*•]\s+", s):
            _runy(d.add_paragraph(style="List Bullet"), re.sub(r"^[-*•]\s+", "", s))
        elif re.match(r"^\d+[.)]\s+", s):
            _runy(d.add_paragraph(style="List Number"), re.sub(r"^\d+[.)]\s+", "", s))
        else:
            _runy(d.add_paragraph(), s)
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()
