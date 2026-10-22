# -*- coding: utf-8 -*-
"""Convert a .docx commentary into HTML matching the Google-Docs export style
used across content/export.json chapters.

Output shape (per the existing chapters):
    <p class="...">
      <span class="...">text</span>
      ...
    </p>

Formatting is reduced to a small, stable set of generated CSS classes rather
than reproducing the opaque per-document .cNN churn. The class set is emitted
alongside the HTML (as the chapter `css`), so the chapter template renders it
identically to the originals.

Classes:
    .p     base paragraph
    .pc    centered paragraph
    .pe    empty spacer paragraph
    .s     base run span
    .b     bold
    .i     italic
    .bi    bold + italic
    .u     underline
    .sup   superscript
    .sub   subscript
    .hN    heading-ish bold span sizes (big/medium)
"""
from __future__ import annotations

import html
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

# Generated CSS block shared by every converted chapter.
CSS = """.p{
color:#000000;
font-size:11pt;
font-family:"Arial";
line-height:1.5;
text-align:justify;
margin:0 0 8pt;
}
.pc{text-align:center;}
.pe{margin:0 0 8pt;min-height:11pt;}
.s{
color:#000000;
font-size:11pt;
font-family:"Arial";
vertical-align:baseline;
}
.b{font-weight:700;}
.i{font-style:italic;}
.bi{font-weight:700;font-style:italic;}
.u{text-decoration:underline;}
.sup{vertical-align:super;font-size:8pt;}
.sub{vertical-align:sub;font-size:8pt;}
.h1{font-weight:700;font-size:16pt;}
.h2{font-weight:700;font-size:13pt;}
.tbl{border-collapse:collapse;margin:8pt 0;}
.tbl td{border:1px solid #cccccc;padding:4pt 6pt;vertical-align:top;}
"""

# docx font sizes are in EMU-ish Pt objects; use .pt for points.
_BIG = 15.0      # >= 15pt bold standalone -> h1
_MED = 12.5      # >= 12.5pt bold standalone -> h2


def _esc(t: str) -> str:
    return html.escape(t, quote=False)


def _run_class(run, para_bold_size_pt):
    """Return the span class string for a run's formatting."""
    b = bool(run.bold)
    i = bool(run.italic)
    u = bool(run.underline)
    sup = bool(run.font.superscript)
    sub = bool(run.font.subscript)
    classes = ["s"]
    if b and i:
        classes.append("bi")
    elif b:
        classes.append("b")
    elif i:
        classes.append("i")
    if u:
        classes.append("u")
    if sup:
        classes.append("sup")
    elif sub:
        classes.append("sub")
    return " ".join(classes)


def _para_size_pt(para):
    sizes = [r.font.size.pt for r in para.runs if r.font.size is not None]
    return max(sizes) if sizes else None


def _emit_paragraph(para) -> str:
    runs = para.runs
    text_all = para.text
    # Empty / whitespace-only paragraph -> spacer.
    if not text_all.strip():
        return '<p class="pe"><span class="s"></span></p>'

    align = para.alignment
    pclass = "p"
    if align == WD_ALIGN_PARAGRAPH.CENTER:
        pclass = "p pc"

    parts = [f'<p class="{pclass}">']
    for r in runs:
        if r.text == "":
            continue
        cls = _run_class(r, None)
        # Preserve internal line breaks within a run.
        seg = _esc(r.text).replace("\n", "<br/>")
        parts.append(f'<span class="{cls}">{seg}</span>')
    parts.append("</p>")
    return "".join(parts)


def _emit_table(tbl: Table) -> str:
    out = ['<table class="tbl"><tbody>']
    for row in tbl.rows:
        out.append("<tr>")
        for cell in row.cells:
            out.append('<td>')
            inner = []
            for p in cell.paragraphs:
                inner.append(_emit_paragraph(p))
            out.append("".join(inner))
            out.append("</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _iter_block_items(doc):
    """Yield Paragraph and Table objects in document order."""
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, doc)
        elif child.tag == qn('w:tbl'):
            yield Table(child, doc)


def convert(path: str) -> str:
    """Return HTML body for the docx at `path` (no <html>/<body> wrapper)."""
    doc = Document(path)
    pieces = []
    for block in _iter_block_items(doc):
        if isinstance(block, Table):
            pieces.append(_emit_table(block))
        else:
            pieces.append(_emit_paragraph(block))
    return "\n".join(pieces)


if __name__ == "__main__":
    import sys, io
    import docx_map
    cid = int(sys.argv[1]) if len(sys.argv) > 1 else 29
    p = docx_map.resolve_path(docx_map.CHAPTER_DOCX[cid])
    html_out = convert(p)
    io.open(r'C:\src\cpbi\_conv_out.html', 'w', encoding='utf-8').write(
        "<style>" + CSS + "</style>\n" + html_out)
    print("len", len(html_out))
