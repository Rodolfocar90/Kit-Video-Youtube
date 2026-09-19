"""Conversor Markdown -> HTML mínimo y sin dependencias.

Cubre lo que generan las skills del kit: títulos, listas, tablas, citas,
negrita/cursiva, código, enlaces y separadores. Todo el texto se escapa
antes de convertirse, así que el HTML de salida es seguro aunque el
Markdown venga con etiquetas.
"""
from __future__ import annotations

import html
import re

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
_ITALIC = re.compile(r"(?<![\*\w])\*([^*\n]+?)\*(?!\*)")
_CODE = re.compile(r"`([^`]+?)`")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_BARE_URL = re.compile(r"(?<!['\"(=])\b(https?://[^\s<>)\]]+)")

# Etiquetas de procedencia: se resaltan como "chips" de color.
TAGS = {
    "[FUENTE DEL VÍDEO]": "tag-video",
    "[FUENTE DEL VIDEO]": "tag-video",
    "[FUENTE EXTERNA]": "tag-extern",
    "[INFERENCIA]": "tag-infer",
    "[NO VERIFICADO]": "tag-warn",
    "CONFIRMADO": "tag-ok",
    "DESMENTIDO": "tag-warn",
    "MATIZADO": "tag-infer",
    "SIN DATOS": "tag-warn",
}


def _inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = _CODE.sub(r"<code>\1</code>", out)
    out = _LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)
    out = _BARE_URL.sub(r'<a href="\1" target="_blank" rel="noopener">\1</a>', out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITALIC.sub(r"<em>\1</em>", out)
    for label, css in TAGS.items():
        escaped = html.escape(label, quote=False)
        if escaped in out:
            out = out.replace(escaped, f'<span class="tag {css}">{escaped}</span>')
    return out


def _flush_list(buffer: list[str], ordered: bool, parts: list[str]) -> None:
    if not buffer:
        return
    tag = "ol" if ordered else "ul"
    items = "".join(f"<li>{item}</li>" for item in buffer)
    parts.append(f"<{tag}>{items}</{tag}>")
    buffer.clear()


def _table(rows: list[str]) -> str:
    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    header = cells(rows[0])
    body = [cells(r) for r in rows[2:]] if len(rows) > 2 else []
    head_html = "".join(f"<th>{_inline(c)}</th>" for c in header)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>" for row in body
    )
    return (f'<div class="tabla"><table><thead><tr>{head_html}</tr></thead>'
            f"<tbody>{body_html}</tbody></table></div>")


def to_html(text: str) -> str:
    """Convierte Markdown a un fragmento HTML."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # quita comentarios HTML
    lines = text.replace("\r\n", "\n").split("\n")
    parts: list[str] = []
    list_buffer: list[str] = []
    list_ordered = False
    quote_buffer: list[str] = []
    table_buffer: list[str] = []
    in_code = False
    code_buffer: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            parts.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_quote() -> None:
        if quote_buffer:
            inner = "".join(f"<p>{_inline(q)}</p>" for q in quote_buffer)
            parts.append(f"<blockquote>{inner}</blockquote>")
            quote_buffer.clear()

    def flush_table() -> None:
        if table_buffer:
            parts.append(_table(table_buffer))
            table_buffer.clear()

    def flush_all() -> None:
        flush_paragraph()
        _flush_list(list_buffer, list_ordered, parts)
        flush_quote()
        flush_table()

    for raw in lines:
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if in_code:
                parts.append("<pre><code>"
                             + html.escape("\n".join(code_buffer), quote=False)
                             + "</code></pre>")
                code_buffer.clear()
            else:
                flush_all()
            in_code = not in_code
            continue
        if in_code:
            code_buffer.append(raw)
            continue

        if not line.strip():
            flush_all()
            continue

        if re.match(r"^\s*(?:[-*_]\s*){3,}$", line):
            flush_all()
            parts.append("<hr>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_all()
            level = len(heading.group(1))
            content = heading.group(2).strip().rstrip("#").strip()
            anchor = re.sub(r"[^\w]+", "-", content.lower()).strip("-")[:60]
            parts.append(f'<h{level} id="{anchor}">{_inline(content)}</h{level}>')
            continue

        if "|" in line and line.strip().startswith("|"):
            flush_paragraph()
            _flush_list(list_buffer, list_ordered, parts)
            flush_quote()
            table_buffer.append(line)
            continue
        flush_table()

        if line.lstrip().startswith(">"):
            flush_paragraph()
            _flush_list(list_buffer, list_ordered, parts)
            quote_buffer.append(line.lstrip().lstrip(">").strip())
            continue
        flush_quote()

        bullet = re.match(r"^\s*[-*+]\s+(.*)$", line)
        numbered = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if bullet or numbered:
            flush_paragraph()
            ordered = bool(numbered)
            if list_buffer and ordered != list_ordered:
                _flush_list(list_buffer, list_ordered, parts)
            list_ordered = ordered
            list_buffer.append(_inline((bullet or numbered).group(1)))
            continue
        # Continuación "perezosa": una línea suelta justo debajo de un item
        # pertenece a ese item, no es un párrafo nuevo.
        if list_buffer and not paragraph:
            list_buffer[-1] += " " + _inline(line.strip())
            continue
        _flush_list(list_buffer, list_ordered, parts)

        paragraph.append(line.strip())

    if in_code and code_buffer:
        parts.append("<pre><code>" + html.escape("\n".join(code_buffer), quote=False)
                     + "</code></pre>")
    flush_all()
    return "\n".join(parts)
